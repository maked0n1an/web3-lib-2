import random

from web3.types import TxParams, Wei
import web3.exceptions as web3_exceptions

from src.helpers.time_functions import sleep
from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import TokenContractData
from src.libs.async_eth_lib.models.params_types import Web3ContractType
from src.libs.async_eth_lib.models.others import LogStatus
from src.libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from src.libs.async_eth_lib.models.transaction import TxArgs
from src.tasks._common.evm_task import EvmTask
from src.tasks._common.utils import RandomChoiceHelper

from .constants import (
    L0_IDS,
    TestnetBridgeData,
    TestnetBridgeSettings,
    get_testnet_bridge_routes,
)



# region Implementation
class TestnetBridgeImplementation(EvmTask):
    def __init__(self, client: EvmClient):
        super().__init__(client)
        self.data = TestnetBridgeData()

    async def bridge(
        self,
        bridge_info: OperationInfo
    ) -> str:
        is_result = False
        
        contract_address = self.data.contracts[self.client.network.name] \
            [bridge_info.from_token_name]
        dst_chain_id = L0_IDS[bridge_info.to_network_name]
        
        contract = self.client.contract.get_evm_contract(
            address=contract_address,
            abi_or_path=(
                'data', 'abis', 'testnet_bridge', 'oft_abi.json'
            )
        )

        bridge_proposal = await self.init_operation_proposal(bridge_info)
        bridge_proposal = await self.complete_bridge_proposal(
            operation_proposal=bridge_proposal,
            slippage=bridge_info.slippage,
            dst_network_name=bridge_info.to_network_name
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

        fee_wei = await self._get_estimateSendFee(
            dst_chain_id=dst_chain_id,
            contract=contract,
            bridge_proposal=bridge_proposal,
        )

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI('swapAndBridge', args=args.get_tuple()),
            value=fee_wei
        )
        
        if not bridge_proposal.from_token.is_native_token:
            is_approved = await self.approve_interface(
                operation_info=bridge_info,
                token_address=bridge_proposal.from_token,
                tx_params=tx_params,
                amount=bridge_proposal.amount_from,
            )

            if is_approved:
                self.client.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{bridge_proposal.amount_from.Ether} {bridge_proposal.from_token.title}"
                )
                await sleep([8, 15])
        else:
            tx_params['value'] += bridge_proposal.amount_from.Wei      
        
        try:
            tx_params = self.set_all_gas_params(bridge_info, tx_params)

            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt()
            
            rounded_amount_from = round(bridge_proposal.amount_from.Ether, 5)
            is_result = receipt['status']

            if is_result:
                log_status = LogStatus.BRIDGED
                message = f''
            else:
                log_status = LogStatus.FAILED
                message = f'Bridge '

            message += (
                f'{rounded_amount_from} {bridge_info.from_token_name}'
                f' from {self.client.network.name} -> {bridge_info.to_network_name}: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()}'
            )
        except web3_exceptions.ContractCustomError as e:
            message = 'Try to make slippage more'
            log_status = LogStatus.ERROR
        except Exception as e:
            message = str(e)
            log_status = LogStatus.ERROR

        self.client.custom_logger.log_message(log_status, message)

        return is_result

    async def _get_estimateSendFee(
        self,
        dst_chain_id: int,
        contract: Web3ContractType,
        bridge_proposal: OperationProposal,
    ) -> Wei:
        estimate_fee_contract = self.client.contract.get_evm_contract(
            address=await contract.functions.oft().call(),
            abi_or_path=(
                'data', 'abis', 'testnet_bridge', 'get_fee_abi.json'
            )
        )
        
        (fee_wei, _) = await estimate_fee_contract.functions.estimateSendFee(
            dst_chain_id,
            self.client.account.address,
            bridge_proposal.amount_from.Wei,
            False,
            '0x'
        ).call()

        return fee_wei
# endregion Implementation


# region Random function
class TestnetBridge:
    def __init__(self, client: EvmClient):
        self.client = client

    async def bridge(self) -> bool:
        settings = TestnetBridgeSettings()
        bridge_routes = get_testnet_bridge_routes()

        random_networks = list(bridge_routes.keys())
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
            
        if not dst_data:
            self.client.custom_logger.log_message(
                status=LogStatus.WARNING,
                message=(
                    'Failed to bridge: not found enough balance in native or tokens in any network'
                )
            )
            return False

        random_dst_data = random.choice(dst_data)
        operation_info.to_network_name = random_dst_data[0]
        operation_info.to_token_name = random_dst_data[1]
        testnet_bridge = TestnetBridgeImplementation(client)

        return await testnet_bridge.bridge(operation_info)
# endregion Random function
