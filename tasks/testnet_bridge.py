import random

import web3.exceptions as web3_exceptions
from web3.types import TxParams

from data.config import MODULES_SETTINGS_FILE_PATH
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.data.token_contracts import TokenContractData
from libs.async_eth_lib.models.bridge import BridgeContractDataFetcher, NetworkData
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, ParamsTypes, TokenAmount, TokenSymbol
from libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.utils import BaseTask, RandomChoiceHelper, StandardSettings
from tasks.config import get_testnet_bridge_routes

# region Settings
class TestnetBridgeSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)

        self.bridge = StandardSettings(
            settings=settings,
            module_name='testnet_bridge',
            action_name='swap'
        )
# endregion Settings


# region Contracts
class TestnetBridgeContracts:
    ABI = ('data', 'abis', 'testnet_bridge', 'abi.json')
    GET_FEE_ABI_PATH = (
        'data', 'abis', 'testnet_bridge', 'get_fee_abi.json'
    )
    
    ARBITRUM_GET_FEE = RawContract(
        title='LayerZero: GETH Token (Arbitrum GETH_LZ)',
        address='0xdD69DB25F6D620A7baD3023c5d32761D353D3De9',
        abi_path=GET_FEE_ABI_PATH
    )
    
    ARBITRUM_ETH = RawContract(
        title='SwapAndBridgeUniswapV3 (Arbitrum ETH)',
        address='0xfca99f4b5186d4bfbdbd2c542dca2eca4906ba45',
        abi_path=ABI
    )
    
    OPTIMISM_GET_FEE = RawContract(
        title='LayerZero: GETH Token (Optimism GETH_LZ)',
        address='0xdD69DB25F6D620A7baD3023c5d32761D353D3De9',
        abi_path=GET_FEE_ABI_PATH
    )
    
    OPTIMISM_ETH = RawContract(
        title='SwapAndBridgeUniswapV3 (Arbitrum ETH)',
        address='0x8352C746839699B1fc631fddc0C3a00d4AC71A17',
        abi_path=ABI
    )
    
    @classmethod
    def get_contract(cls, contract_name: str):
        return getattr(cls, contract_name)
        
# endregion Contracts


# region Implementation
class TestnetBridgeImplementation(BaseTask):
    async def bridge(
        self,
        bridge_info: OperationInfo
    ) -> str:
        check_message = self.validate_inputs(
            first_arg=self.client.network.name,
            second_arg=bridge_info.to_network.name,
            param_type='networks'
        )
        if check_message:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        
        from_network_name = self.client.network.name.capitalize()
        to_network_name = bridge_info.to_network.name.capitalize()
        
        bridge_raw_contract = TestnetBridgeData.get_only_contract_for_bridge(
            network_name=self.client.network.name,
            token_symbol=bridge_info.from_token_name
        )
        dst_chain_id = TestnetBridgeData.get_chain_id(to_network_name)
        
        contract = await self.client.contract.get(
            contract=bridge_raw_contract
        )

        bridge_proposal = await self.compute_source_token_amount(bridge_info)
        bridge_proposal = await self.compute_min_destination_amount(
            operation_proposal=bridge_proposal,
            min_to_amount=bridge_proposal.amount_from.Wei,
            operation_info=bridge_info,
            is_to_token_price_wei=True
        )

        args = TxArgs(
            _amountIn=bridge_proposal.amount_from.Wei,
            _amountOutMin=bridge_proposal.min_amount_to.Wei,
            _dstChainId=dst_chain_id,
            _to=self.client.account.address,
            _refundAddress=self.client.account.address,
            _zroPaymentAddress=TokenContractData.ZERO_ADDRESS,
            _adapterParams='0x'
        )

        value = await self._get_estimateSendFee(
            dst_chain_id=dst_chain_id,
            contract=contract,
            bridge_proposal=bridge_proposal,
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swapAndBridge', args=args.get_tuple()),
            value=value.Wei
        )
        
        if not bridge_proposal.from_token.is_native_token:
            is_approved = await self.approve_interface(
                operation_info=bridge_info,
                token_contract=bridge_proposal.from_token,
                tx_params=tx_params,
                amount=bridge_proposal.amount_from,
            )

            if is_approved:
                self.client.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{bridge_proposal.amount_from.Ether} {bridge_proposal.from_token.title}"
                )
                await sleep(8, 15)
        else:
            tx_params['value'] += bridge_proposal.amount_from.Wei      
        
        try:
            tx_params = self.set_all_gas_params(
                operation_info=bridge_info,
                tx_params=tx_params
            )

            tx = await self.client.transaction.sign_and_send(
                tx_params=tx_params
            )
            receipt = await tx.wait_for_tx_receipt(
                web3=self.client.w3
            )

            rounded_amount_from = round(bridge_proposal.amount_from.Ether, 5)

            if receipt['status']:
                status = LogStatus.BRIDGED
                message = ''

            else:
                status = LogStatus.FAILED
                message = f'Swap'
            
            if receipt['status']:
                message = f'TestnetBridge | Bridged {rounded_amount_from} {bridge_info.from_token}'
            else:
                message = f'TestnetBridge | Failed bridge {rounded_amount_from} {bridge_info.from_token}'

            message += (
                f'{rounded_amount_from} {bridge_info.from_token_name}'
                f' from {from_network_name} -> {to_network_name}: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()}'
            )

            self.client.custom_logger.log_message(status, message)
                
            return receipt['status']
        except web3_exceptions.ContractCustomError as e:
            status = LogStatus.ERROR
            message = 'Try to make slippage more'
        except Exception as e:
            error = str(e)
            status = LogStatus.ERROR
            message = error

        self.client.custom_logger.log_message(status, message)

        return False

    async def _get_estimateSendFee(
        self,
        dst_chain_id: int,
        contract: ParamsTypes.Web3Contract,
        bridge_proposal: OperationProposal,
    ) -> TokenAmount:
        contract_to_get_fee = await contract.functions.oft().call()

        estimate_fee_contract = await self.client.contract.get(
            contract=contract_to_get_fee,
            abi_or_path=TestnetBridgeContracts.GET_FEE_ABI_PATH
        )
        
        result = await estimate_fee_contract.functions.estimateSendFee(
            dst_chain_id,
            self.client.account.address,
            bridge_proposal.amount_from.Wei,
            False,
            '0x'
        ).call()

        return TokenAmount(amount=result[0], wei=True)
# endregion Implementation


# region Available networks
class TestnetBridgeData(BridgeContractDataFetcher):
    networks_data = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.ETH: TestnetBridgeContracts.ARBITRUM_ETH,
            }
        ),
        Networks.Optimism.name: NetworkData(
            chain_id=111,
            bridge_dict={
                TokenSymbol.ETH: TestnetBridgeContracts.OPTIMISM_ETH,
            }
        ),
        Networks.Sepolia.name: NetworkData(
            chain_id=161,
            bridge_dict={
                #
            }
        )
    }
# endregion Available networks


# region Random function
class TestnetBridge(BaseTask):
    async def bridge(
        self,
    ):
        settings = TestnetBridgeSettings()
        bridge_routes = get_testnet_bridge_routes()

        random_networks = list(bridge_routes.keys())
        random.shuffle(random_networks)

        self.client.custom_logger.log_message(
            status=LogStatus.INFO,
            message='Started to search enough balance for bridge'
        )
        for network in random_networks:
            client = Client(
                account_id=self.client.account_id,
                private_key=self.client.account._private_key,
                network=network,
                proxy=self.client.proxy
            )

            (operation_info, dst_data) = await RandomChoiceHelper.get_random_token_for_operation(
                op_name='bridge',
                op_data=get_testnet_bridge_routes(),
                op_settings=settings.bridge,
                client=client
            )
            
        if not dst_data:
            self.client.custom_logger.log_message(
                status=LogStatus.WARNING,
                message=(
                    'Failed to bridge: not found enough balance in native or tokens in any network'
                )
            )
            return False

        random_dst_data = random.choice(dst_data)
        operation_info.to_network = random_dst_data[0]
        operation_info.to_token_name = random_dst_data[1]
        testnet_bridge = TestnetBridgeImplementation(client)

        return await testnet_bridge.bridge(operation_info)
# endregion Random function
