import random

import web3.exceptions as web3_exceptions
from web3.types import TxParams
from eth_abi import abi

from user_data._inputs.settings._global import MODULES_SETTINGS_FILE_PATH
from libs.async_eth_lib.architecture.client import EvmClient
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.data.token_contracts import TokenContractData
from libs.async_eth_lib.models.bridge import BridgeContractDataFetcher, NetworkData
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, TokenAmount, TokenSymbol
from libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.evm_task import EvmTask
from tasks._common.utils import RandomChoiceHelper, StandardSettings
from tasks.config import get_coredao_bridge_routes


# region Settings
class CoreDaoBridgeSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)
        self.bridge = StandardSettings(
            settings=settings,
            module_name='coredao',
            action_name='bridge'
        )
# endregion Settings


# region Contracts
class CoreDaoBridgeContracts:
    TO_CORE_BRIDGE_ABI = ('data', 'abis', 'coredao', 'to_core_bridge_abi.json')
    FROM_CORE_BRIDGE_ABI = ('data', 'abis', 'coredao', 'from_core_bridge_abi.json')

    BSC = RawContract(
        title='OriginalTokenBridge (BSC)',
        address='0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
        abi_path=TO_CORE_BRIDGE_ABI
    )

    CORE = RawContract(
        title='WrappedTokenBridge (CORE)',
        address='0xA4218e1F39DA4AaDaC971066458Db56e901bcbdE',
        abi_path=FROM_CORE_BRIDGE_ABI
    )

    POLYGON = RawContract(
        title='OriginalTokenBridge (POLYGON)',
        address='0x52e75D318cFB31f9A2EdFa2DFee26B161255B233',
        abi_path=TO_CORE_BRIDGE_ABI
    )

    OPTIMISM = RawContract(
        title='OriginalTokenBridge (OPTIMISM)',
        address='0x29d096cD18C0dA7500295f082da73316d704031A',
        # ShimmerBridge (0x9C6D5a71FdD306329287a835e9B8EDb7F0F17898)
        abi_path=TO_CORE_BRIDGE_ABI
    )

    ARBITRUM = RawContract(
        title='OriginalTokenBridge (ARBITRUM)',
        address='0x29d096cD18C0dA7500295f082da73316d704031A',
        abi_path=TO_CORE_BRIDGE_ABI
    )

    AVALANCHE = RawContract(
        title='OriginalTokenBridge (AVALANCHE)',
        address='0x29d096cD18C0dA7500295f082da73316d704031A',
        abi_path=TO_CORE_BRIDGE_ABI
    )
# endregion Contracts


# region Supported networks
class CoreDaoData(BridgeContractDataFetcher):
    NETWORKS_DATA = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.USDT: CoreDaoBridgeContracts.ARBITRUM,
                TokenSymbol.USDC: CoreDaoBridgeContracts.ARBITRUM
            }
        ),
        Networks.Avalanche.name: NetworkData(
            chain_id=106,
            bridge_dict={
                TokenSymbol.USDT: CoreDaoBridgeContracts.AVALANCHE,
                TokenSymbol.USDC: CoreDaoBridgeContracts.AVALANCHE,
            }
        ),
        Networks.BSC.name: NetworkData(
            chain_id=102,
            bridge_dict={
                TokenSymbol.USDT: CoreDaoBridgeContracts.BSC,
                TokenSymbol.USDC: CoreDaoBridgeContracts.BSC,
            }
        ),
        Networks.Core.name: NetworkData(
            chain_id=153,
            bridge_dict={
                TokenSymbol.USDT: CoreDaoBridgeContracts.CORE,
                TokenSymbol.USDC: CoreDaoBridgeContracts.CORE,
            }
        ),
        Networks.Optimism.name: NetworkData(
            chain_id=111,
            bridge_dict={
                TokenSymbol.USDT: CoreDaoBridgeContracts.OPTIMISM,
                TokenSymbol.USDC: CoreDaoBridgeContracts.OPTIMISM,
            }
        ),
        Networks.Polygon.name: NetworkData(
            chain_id=109,
            bridge_dict={
                TokenSymbol.USDT: CoreDaoBridgeContracts.POLYGON,
                TokenSymbol.USDC: CoreDaoBridgeContracts.POLYGON,
            }
        ),
    }

    AVAILABLE_COINS_FOR_BRIDGE = [TokenSymbol.USDT, TokenSymbol.USDC]
# endregion Supported networks


# region Implementation
class CoreDaoBridgeImplementation(EvmTask):
    async def bridge(self, bridge_info: OperationInfo) -> str:
        from_network_name = self.client.network.name
        to_network_name = bridge_info.to_network.name

        bridge_raw_contract = CoreDaoData.get_only_contract_for_bridge(
            network_name=from_network_name,
            token_symbol=bridge_info.from_token_name
        )

        bridge_proposal = await self.init_operation_proposal(bridge_info)
        bridge_proposal = await self.complete_operation_proposal(
            operation_proposal=bridge_proposal,
            slippage=bridge_info.slippage,
        )
        tx_params = await self._prepare_params(
            bridge_raw_contract, bridge_proposal, bridge_info
        )

        if not tx_params['value']:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=f'Can not get fee to bridge in {from_network_name}',
                call_depth_or_custom_call_place='CoreDaoBridge'
            )
            return is_result

        native_balance = TokenAmount(
            amount=await self.client.contract.get_balance(),
            decimals=self.client.network.decimals,
            wei=True
        )
        value = TokenAmount(
            amount=tx_params['value'],
            decimals=self.client.network.decimals,
            wei=True
        )

        if native_balance.Wei < value.Wei:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Too low balance: '
                    f'balance - {round(native_balance.Ether, 5)} '
                    f'{self.client.network.coin_symbol}; '
                    f'needed fee to bridge - {round(value.Ether, 5)} '
                    f'{self.client.network.coin_symbol};'
                )
            )
            return is_result

        if not bridge_proposal.from_token.is_native_token:
            is_approved = await self.approve_interface(
                operation_info=bridge_info,
                token_address=bridge_proposal.from_token.address,
                tx_params=tx_params,
                amount=bridge_proposal.amount_from,
            )

            if is_approved:
                self.client.custom_logger.log_message(
                    status=LogStatus.APPROVED,
                    message=(
                        f'{bridge_proposal.amount_from.Ether} '
                        f'{bridge_proposal.from_token.title}'
                    )
                )
                await sleep(20, 50)
        else:
            tx_params['value'] += bridge_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                operation_info=bridge_info,
                tx_params=tx_params
            )
            
            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt(web3=self.client.w3, timeout=300)
            is_result = receipt['status']
            
            if is_result:
                status = LogStatus.BRIDGED
                message = ''
                
            else:
                status = LogStatus.FAILED
                message = f'Bridge'

            rounded_amount_from = round(bridge_proposal.amount_from.Ether, 5)
            
            message += (
                f'{rounded_amount_from} {bridge_info.from_token_name} '
                f'from {from_network_name} -> {rounded_amount_from} '
                f'{bridge_info.to_token_name} in {to_network_name}: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()}'
            )
        except web3_exceptions.ContractCustomError as e:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message='Failed to bridge, trying to make slippage more...'
            )
            bridge_info.slippage *= 1.3
            return await self.bridge(bridge_info)
        except Exception as e:
            status=LogStatus.ERROR
            message=str(e)

        self.client.custom_logger.log_message(status, message)
        return is_result

    async def _prepare_params(
        self,
        bridge_raw_contract: RawContract,
        bridge_proposal: OperationProposal,
        bridge_info: OperationInfo,
    ) -> TxParams:
        contract = self.client.contract.get_evm_contract_from_raw(
            bridge_raw_contract
        )
        
        callParams = TxArgs(
            refundAddress=self.client.account.address,
            zroPaymentAddress=TokenContractData.ZERO_ADDRESS
        )
        
        if self.client.network == Networks.Optimism:
            adapter_params = abi.encode(["uint8", "uint64"], [1, 100000])
            adapter_params = self.client.w3.to_hex(adapter_params[30:])
        else:
            adapter_params = '0x'

        if self.client.network == Networks.Core:
            dst_chain_id = CoreDaoData.get_chain_id(
                network_name=bridge_info.to_network.name
            )

            args = TxArgs(
                localToken=bridge_proposal.from_token.address,
                remoteChainId=dst_chain_id,
                amount=bridge_proposal.amount_from.Wei,
                to=self.client.account.address,
                unwrapWeth=False,
                callParams=callParams.get_tuple(),
                adapterParams=adapter_params
            )

            result = await contract.functions.estimateBridgeFee(
                dst_chain_id,
                False,
                adapter_params
            ).call()
        else:
            args = TxArgs(
                token=bridge_proposal.from_token.address,
                amountLd=bridge_proposal.amount_from.Wei,
                to=self.client.account.address,
                callParams=callParams.get_tuple(),
                adapterParams=adapter_params
            )

            result = await contract.functions.estimateBridgeFee(
                False,
                adapter_params
            ).call()

        fee = TokenAmount(
            amount=result[0],
            decimals=self.client.network.decimals,
            wei=True
        )
        multiplier = 1.03
        fee.Wei = int(fee.Wei * multiplier)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                'bridge',
                args=args.get_tuple(),
            ),
            value=fee.Wei
        )

        return tx_params
# endregion Implementation


# region Random function
class CoreDaoBridge:
    def __init__(self, client: EvmClient):
        self.client = client

    async def bridge(self) -> bool:
        settings = CoreDaoBridgeSettings()
        bridge_routes = get_coredao_bridge_routes()

        random_networks = list(bridge_routes)
        random.shuffle(random_networks)

        self.client.custom_logger.log_message(
            status=LogStatus.INFO,
            message='Started to search enough balance for bridge'
        )
        
        for network in random_networks:
            client = EvmClient(
                account_id=self.client.account_id,
                private_key=self.client.account._private_key,
                network=network,
                proxy=self.client.proxy
            )
        
            (operation_info, dst_data) = await RandomChoiceHelper.get_partial_operation_info_and_dst_data(
                op_data=bridge_routes,
                op_settings=settings.bridge,
                client=client
            )
            
            if operation_info:
                break

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
        coredao_bridge = CoreDaoBridgeImplementation(client)

        return await coredao_bridge.bridge(operation_info)
# endregion Random function
