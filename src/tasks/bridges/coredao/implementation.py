import random

import web3.exceptions as web3_exceptions
from web3.types import TxParams
from eth_abi import abi

from _types.networks import NetworkNames
from src.helpers.time_functions import sleep
from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import TokenContractData
from src.libs.async_eth_lib.models.others import LogStatus, TokenAmount
from src.libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from src.libs.async_eth_lib.models.transaction import TxArgs
from src.tasks._common.evm_task import EvmTask
from src.tasks._common.utils import PriceUtils, RandomChoiceHelper

from .constants import (
    CoreDaoBridgeABIs,
    CoreDaoBridgeData,
    CoreDaoBridgeSettings,
    L0_IDS,
    get_coredao_bridge_routes
)


# region Implementation
class CoreDaoBridgeImplementation(EvmTask):
    def __init__(self, client: EvmClient):
        super().__init__(client)
        self.data = CoreDaoBridgeData()

    async def bridge(
        self,
        bridge_info: OperationInfo,
        max_fee: float = 0.7,
    ) -> str:
        from_network_name = self.client.network.name
        to_network_name = bridge_info.to_network_name

        contract_address = self.data.contracts[from_network_name][bridge_info.from_token_name]

        bridge_proposal = await self.init_operation_proposal(bridge_info)
        bridge_proposal = await self.complete_bridge_proposal(
            operation_proposal=bridge_proposal,
            slippage=bridge_info.slippage,
            dst_network_name=bridge_info.to_network_name
        )

        tx_params = await self._get_data_for_bridge(
            bridge_info=bridge_info,
            bridge_proposal=bridge_proposal,
            bridge_address=contract_address
        )

        if 'value' not in tx_params:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Can not get value for ({self.client.network.name})'
                )
            )
            return is_result

        value = TokenAmount(
            amount=tx_params['value'],
            decimals=self.client.network.decimals,
            wei=True
        )

        if not await self._check_for_enough_balance(value):
            return is_result

        token_price = await PriceUtils.get_cex_price(
            first_token=self.client.network.coin_symbol
        )
        network_fee = float(value.Ether) * token_price

        if network_fee > max_fee:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Too high fee for bridge: max. fee: '
                    f'{max_fee}; value: {value.Ether}'
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
                await sleep([20, 50])
        else:
            tx_params['value'] += bridge_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                operation_info=bridge_info,
                tx_params=tx_params
            )

            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt(timeout=300)

            rounded_amount_from = round(bridge_proposal.amount_from.Ether, 5)
            is_result = receipt['status']

            if is_result:
                status = LogStatus.BRIDGED
                message = ''

            else:
                status = LogStatus.FAILED
                message = f'Bridge'

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
            bridge_info.slippage *= 1.2
            return await self.bridge(bridge_info)
        except Exception as e:
            status = LogStatus.ERROR
            message = str(e)

        self.client.custom_logger.log_message(status, message)
        return is_result

    async def _get_data_for_bridge(
        self,
        bridge_info: OperationInfo,
        bridge_proposal: OperationProposal,
        bridge_address: str,
    ) -> TxParams:
        l0_multiplier = 1.03
        callParams = TxArgs(
            refundAddress=self.client.account.address,
            zroPaymentAddress=TokenContractData.ZERO_ADDRESS
        )

        if self.client.network.name == NetworkNames.Core:
            contract = self.client.contract.get_evm_contract(
                address=bridge_address,
                abi_or_path=CoreDaoBridgeABIs.FROM_CORE_BRIDGE_ABI
            )
            dst_chain_id = L0_IDS['v1'][bridge_info.to_network_name]

            args = TxArgs(
                localToken=bridge_proposal.from_token.address,
                remoteChainId=dst_chain_id,
                amount=bridge_proposal.amount_from.Wei,
                to=self.client.account.address,
                unwrapWeth=False,
                callParams=callParams.get_tuple(),
                adapterParams=adapter_params
            )

            (fee_wei, _) = await contract.functions.estimateBridgeFee(
                dst_chain_id,
                False,
                adapter_params
            ).call()
        else:
            if self.client.network.name == NetworkNames.Optimism:
                adapter_params = abi.encode(["uint8", "uint64"], [1, 100000])
                adapter_params = self.client.w3.to_hex(adapter_params[30:])
            else:
                adapter_params = '0x'

            contract = self.client.contract.get_evm_contract(
                address=bridge_address,
                abi_or_path=CoreDaoBridgeABIs.TO_CORE_BRIDGE_ABI
            )
            
            args = TxArgs(
                token=bridge_proposal.from_token.address,
                amountLd=bridge_proposal.amount_from.Wei,
                to=self.client.account.address,
                callParams=callParams.get_tuple(),
                adapterParams=adapter_params
            )

            (fee_wei, _) = await contract.functions.estimateBridgeFee(
                False,
                adapter_params
            ).call()

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                'bridge',
                args=args.get_tuple(),
            ),
            value=int(fee_wei * l0_multiplier)
        )

        return tx_params

    async def _check_for_enough_balance(
        self,
        fee_amount: TokenAmount
    ) -> bool:
        native_balance = TokenAmount(
            amount=await self.client.contract.get_balance(),
            decimals=self.client.network.decimals,
            wei=True
        )
        if native_balance.Wei > fee_amount.Wei:
            return True

        coin_symbol = self.client.network.coin_symbol

        self.client.custom_logger.log_message(
            status=LogStatus.ERROR,
            message=(
                f'Too low balance: balance - '
                f'{round(native_balance.Ether, 5)} {coin_symbol}; '
                f'bridge fee - {round(fee_amount.Ether, 5)} {coin_symbol};'
            )
        )

        return False
# endregion Implementation


# region Random function
class CoreDaoBridge(EvmTask):
    async def bridge(self) -> bool:
        settings = CoreDaoBridgeSettings()
        bridge_routes = get_coredao_bridge_routes()

        random_networks = list(bridge_routes)
        random.shuffle(random_networks)

        self.client.custom_logger.log_message(
            status=LogStatus.INFO,
            message='Started to search enough balance for bridge'
        )
 
        for network_name in random_networks:
            client = EvmClient(
                account_id=self.client.account_id,
                private_key=self.client.account._private_key,
                network_name=network_name,
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
        operation_info.to_network_name = random_dst_data[0]
        operation_info.to_token_name = random_dst_data[1]
        coredao_bridge = CoreDaoBridgeImplementation(client)

        return await coredao_bridge.bridge(operation_info)
# endregion Random function
