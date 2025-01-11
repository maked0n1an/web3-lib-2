import random

from eth_abi import abi
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from src.helpers.time_functions import sleep

from .constants import (
    L0_IDS,
    POOL_IDS,
    BridgeType,
    StargateABIs,
    StargateData,
    StargateSettings,
    get_stargate_routes
)
from src._types.tokens import TokenSymbol
from src.libs.async_eth_lib.data.networks import Networks
from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import TokenContractData
from src.libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from src.libs.async_eth_lib.models.others import LogStatus, TokenAmount
from src.libs.async_eth_lib.models.params_types import Web3ContractType
from src.libs.async_eth_lib.models.transaction import TxArgs
from src.tasks._common.evm_task import EvmTask
from src.tasks._common.utils import HexUtils, PriceUtils, RandomChoiceHelper


class StargateImplementation(EvmTask):
    def __init__(self, client: EvmClient):
        super().__init__(client)
        self.data = StargateData()

    async def bridge_v1(
        self,
        bridge_info: OperationInfo,
        max_fee: float = 0.7,
        dst_fee: float | TokenAmount | None = None
    ) -> bool:
        is_result = False
        bridge_proposal = await self.init_operation_proposal(bridge_info)
        bridge_proposal = await self.complete_bridge_proposal(
            operation_proposal=bridge_proposal,
            slippage=bridge_info.slippage,
            dst_network=bridge_info.to_network
        )

        tx_params = await self._get_data_for_crosschain_swap_v1(
            bridge_info=bridge_info,
            bridge_proposal=bridge_proposal,
            dst_fee=dst_fee
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

        dst_native_amount_price = 0
        if dst_fee:
            dst_native_token_price = await PriceUtils.get_cex_price(
                bridge_info.to_network.coin_symbol
            )
            dst_native_amount_price = (
                float(dst_fee.Ether) * dst_native_token_price
            )

        if network_fee - dst_native_amount_price > max_fee:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Too high fee for bridge: max. fee: '
                    f'{max_fee}; value: {value.Ether}'
                )
            )

            return is_result

        if not bridge_proposal.from_token.is_native_token:
            optional_tx_hash = await self.approve_interface(
                operation_info=bridge_info,
                token_address=bridge_proposal.from_token.address,
                tx_params=tx_params,
                amount=bridge_proposal.amount_from,
            )

            if optional_tx_hash:
                self.client.custom_logger.log_message(
                    status=LogStatus.APPROVED,
                    message=(
                        f'{bridge_proposal.from_token.title}'
                        f'{bridge_proposal.amount_from.Ether}'
                    )
                )
                await sleep(10, 30)
        else:
            tx_params['value'] += bridge_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                operation_info=bridge_info,
                tx_params=tx_params
            )

            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt(self.client.w3, timeout=240)

            rounded_amount_from = round(bridge_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(bridge_proposal.min_amount_to.Ether, 5)
            is_result = receipt['status']

            if is_result:
                log_status = LogStatus.BRIDGED
                message = 'V1 '
            else:
                log_status = LogStatus.FAILED
                message = f'Bridge V1 '

            message += (
                f'{rounded_amount_from} {bridge_info.from_token_name} '
                f'from {self.client.network.name} -> {rounded_amount_to} '
                f'{bridge_info.to_token_name} in {bridge_info.to_network.name}: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()}'
            )
        except web3_exceptions.ContractCustomError as e:
            message = 'V1: Try to make slippage more'
            log_status = LogStatus.ERROR
        except Exception as e:
            message = str(e)
            log_status = LogStatus.ERROR

        self.client.custom_logger.log_message(log_status, message)

        return is_result

    async def bridge_v2(
        self,
        bridge_info: OperationInfo,
        bridge_type: BridgeType = BridgeType.Economy,
        max_fee: float = 0.7,
    ) -> bool:
        is_result = False
        bridge_proposal = await self.init_operation_proposal(bridge_info)
        bridge_proposal = await self.complete_bridge_proposal(
            operation_proposal=bridge_proposal,
            slippage=bridge_info.slippage,
            dst_network=bridge_info.to_network
        )

        tx_params = await self._get_data_for_crosschain_swap_v2(
            bridge_info=bridge_info,
            bridge_proposal=bridge_proposal,
            bridge_type=bridge_type
        )

        bridge_fee = TokenAmount(
            amount=tx_params['value'],
            decimals=self.client.network.decimals,
            wei=True
        )

        if not await self._check_for_enough_balance(bridge_fee):
            return is_result

        token_price = await PriceUtils.get_cex_price(
            first_token=self.client.network.coin_symbol
        )
        network_fee = float(bridge_fee.Ether) * token_price

        if network_fee > max_fee:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Too high fee for bridge: max. fee: '
                    f'{max_fee}; value: {bridge_fee.Ether}'
                )
            )

            return is_result

        if not bridge_proposal.from_token.is_native_token:
            optional_tx_hash = await self.approve_interface(
                operation_info=bridge_info,
                token_address=bridge_proposal.from_token.address,
                tx_params=tx_params,
                amount=bridge_proposal.amount_from
            )

            if optional_tx_hash:
                self.client.custom_logger.log_message(
                    status=LogStatus.APPROVED,
                    message=(
                        f'{bridge_proposal.from_token.title} '
                        f'{bridge_proposal.amount_from.Ether}'
                    )
                )
                await sleep(10, 30)
        else:
            tx_params['value'] += bridge_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(bridge_info, tx_params)

            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt(self.client.w3)

            rounded_amount_from = round(bridge_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(bridge_proposal.min_amount_to.Ether, 5)
            is_result = receipt['status']

            if is_result:
                status = LogStatus.BRIDGED
                message = f'V2 \'{bridge_type.name}\' '

                # await self._add_bridge_to_db(
                #     bridge_info=bridge_info,
                #     bridge_proposal=bridge_proposal,
                #     bridge_fee=bridge_fee,
                #     token_price=token_price,
                #     tx_hash=tx.hash.hex(),
                #     platform='Stargate'
                # )
            else:
                status = LogStatus.FAILED
                message = f'Bridge V2 \'{bridge_type.name}\' '

            message += (
                f'{rounded_amount_from} {bridge_info.from_token_name} '
                f'from {self.client.network.name} -> {rounded_amount_to} '
                f'{bridge_info.to_token_name} in {bridge_info.to_network.name}'
            )
        except web3_exceptions.ContractCustomError as e:
            message = 'V2: Try to make slippage more'
            status = LogStatus.ERROR
        except Exception as e:
            error = 'insufficient funds for gas + value'
            if error in str(e):
                message = error.capitalize()

            else:
                message = str(e)

            status = LogStatus.ERROR

        self.client.custom_logger.log_message(status, message)

        return is_result

    async def _get_data_for_crosschain_swap_v1(
        self,
        bridge_info: OperationInfo,
        bridge_proposal: OperationProposal,
        dst_fee: TokenAmount | None = None
    ) -> TxParams:
        dst_chain_id = L0_IDS['v1'][bridge_info.to_network.name]
        contract_address = self.data.get_contract_address(
            network=self.client.network.name,
            from_token=bridge_info.from_token_name,
            to_token=bridge_info.to_token_name,
            version='v1'
        )
        l0_multiplier_fee = 1.06
        self_address = self.client.account.address

        if bridge_info.from_token_name == TokenSymbol.ETH:
            router_contract = self.client.contract.get_evm_contract(
                address=contract_address,
                abi_or_path=StargateABIs.ROUTER_ETH_V1_ABI
            )
            call_contract = self.client.contract.get_evm_contract(
                address=await router_contract.functions.stargateRouter().call(),
                abi_or_path=StargateABIs.ROUTER_V1_ABI
            )

            (fee_wei, _) = await self._quote_layer_zero_fee(
                router_contract=call_contract,
                dst_chain_id=dst_chain_id,
            )

            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _refundAddress=self_address,
                _toAddress=self_address,
                _amountLD=bridge_proposal.amount_from.Wei,
                _minAmountLd=bridge_proposal.min_amount_to.Wei,
            )

            function_name = 'swapETH'
        elif (
            bridge_info.from_token_name == TokenSymbol.USDV
            and bridge_info.to_token_name == TokenSymbol.USDV
        ):
            router_contract = self.client.contract.get_evm_contract(
                address=contract_address,
                abi_or_path=StargateABIs.ROUTER_V1_ABI
            )
            msg_contract = self.client.contract.get_evm_contract(
                address=await router_contract.functions.getRole(3).call(),
                abi_or_path=StargateABIs.MESSAGING_V1_ABI
            )

            min_gas_limit = await msg_contract.functions.minDstGasLookup(
                dst_chain_id,
                1
            ).call()

            adapter_params = abi.encode(
                ["uint16", "uint64"], [1, min_gas_limit])
            adapter_params = self.client.w3.to_hex(adapter_params[30:])

            fee_wei = await self._quote_send_fee(
                router_contract=router_contract,
                bridge_proposal=bridge_proposal,
                adapter_params=adapter_params,
                dst_chain_id=dst_chain_id
            )

            tx_args = TxArgs(
                _param=TxArgs(
                    to=HexUtils.to_cut_hex_prefix_and_zfill(self_address),
                    amountLD=bridge_proposal.amount_from.Wei,
                    minAmountLD=bridge_proposal.min_amount_to.Wei,
                    dstEid=dst_chain_id
                ).get_tuple(),
                _extraOptions=adapter_params,
                _msgFee=TxArgs(
                    nativeFee=int(fee_wei * l0_multiplier_fee),
                    lzTokenFee=0
                ).get_tuple(),
                _refundAddress=self_address,
                _composeMsg='0x'
            )

            function_name = 'send'
        elif (
            bridge_info.from_token_name != TokenSymbol.USDV  # region Not works Token -> USDV
            and bridge_info.to_token_name == TokenSymbol.USDV
        ):
            router_contract = self.client.contract.get_evm_contract(
                address=contract_address,
                abi_or_path=StargateABIs.BRIDGE_RECOLOR
            )

            lz_tx_params = TxArgs(
                lvl=1,
                limit=170000
            )

            adapter_params = abi.encode(
                ["uint16", "uint64"],
                lz_tx_params.get_list()
            )
            adapter_params = self.client.w3.to_hex(adapter_params[30:])

            recolor_contract = self.client.contract.get_evm_contract_from_raw(
                bridge_proposal.to_token
            )

            fee_wei = await self._quote_send_fee(
                router_contract=recolor_contract,
                bridge_proposal=bridge_proposal,
                adapter_params=adapter_params,
                dst_chain_id=dst_chain_id
            )

            tx_args = TxArgs(
                _swapParam=TxArgs(
                    _fromToken=bridge_proposal.from_token.address,
                    _fromTokenAmount=bridge_proposal.amount_from.Wei,
                    _minUSDVOut=bridge_proposal.min_amount_to.Wei
                ).get_tuple(),
                _color=await router_contract.functions.color().call(),
                _param=TxArgs(
                    to=HexUtils.to_cut_hex_prefix_and_zfill(self_address),
                    amountLD=bridge_proposal.amount_from.Wei,
                    minAmountLD=bridge_proposal.min_amount_to.Wei,
                    dstEid=dst_chain_id
                ).get_tuple(),
                _extraOptions=adapter_params,
                _msgFee=TxArgs(
                    nativeFee=int(fee_wei * l0_multiplier_fee),
                    lzTokenFee=0
                ).get_tuple(),
                _refundAddress=self_address,
                _composeMsg='0x'
            )
            function_name = 'swapRecolorSend'

        elif bridge_info.from_token_name == TokenSymbol.STG:
            router_contract = self.client.contract.get_evm_contract(
                address=contract_address,
                abi_or_path=StargateABIs.STG_ABI
            )

            lz_tx_params = TxArgs(
                lvl=1,
                limit=85000
            )
            adapter_params = abi.encode(
                ["uint16", "uint64"],
                lz_tx_params.get_list()
            )
            adapter_params = self.client.w3.to_hex(adapter_params[30:])

            fee_wei = await router_contract.functions.estimateSendTokensFee(
                dst_chain_id,
                False,
                adapter_params
            ).call()

            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _to=self_address,
                _qty=bridge_proposal.amount_from.Wei,
                zroPaymentAddress=TokenContractData.ZERO_ADDRESS,
                adapterParam=adapter_params
            )
            function_name = 'sendTokens'

        else:
            router_contract = self.client.contract.get_evm_contract(
                address=contract_address,
                abi_or_path=StargateABIs.ROUTER_V1_ABI
            )

            (fee_wei, lz_tx_params) = await self._quote_layer_zero_fee(
                router_contract=router_contract,
                dst_chain_id=dst_chain_id,
                dst_fee=dst_fee
            )

            src_pool_id = POOL_IDS[self.client.network.name].get(
                [bridge_info.from_token_name]
            )
            dst_pool_id = POOL_IDS[bridge_info.to_network.name].get(
                [bridge_info.to_token_name]
            )

            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _srcPoolId=src_pool_id,
                _dstPoolId=dst_pool_id,
                _refundAddress=self_address,
                _amountLD=bridge_proposal.amount_from.Wei,
                _minAmountLd=bridge_proposal.min_amount_to.Wei,
                _lzTxParams=lz_tx_params.get_tuple(),
                _to=self_address,
                _payload='0x'
            )
            function_name = 'swap'

        tx_params = TxParams(
            to=router_contract.address,
            data=router_contract.encodeABI(
                function_name,
                args=tx_args.get_tuple()
            ),
            value=int(fee_wei * l0_multiplier_fee)
        )

        return tx_params

    async def _get_data_for_crosschain_swap_v2(
        self,
        bridge_info: OperationInfo,
        bridge_proposal: OperationProposal,
        bridge_type: BridgeType
    ) -> TxParams:
        dst_chain_id = L0_IDS['v2'][bridge_info.to_network.name]
        self_address = self.client.account.address
        contract_address = self.data.get_contract_address(
            network=self.client.network.name,
            from_token=bridge_info.from_token_name,
            to_token=bridge_info.to_token_name,
            version='v2'
        )

        bridge_contract = self.client.contract.get_evm_contract(
            address=contract_address,
            abi_or_path=StargateABIs.V2_ABI
        )

        _sendParams = TxArgs(
            dstEid=dst_chain_id,
            to=HexUtils.zfill_hex_value(self_address),
            amountLd=bridge_proposal.amount_from.Wei,
            minAmountLd=bridge_proposal.min_amount_to.Wei,
            extraOptions='0x',
            composeMsg='0x',
            oftCmd=bridge_type.value
        )

        bridge_fee_wei, _ = await bridge_contract.functions.quoteSend(
            _sendParams.get_tuple(),
            False
        ).call()

        tx_args = TxArgs(
            _sendParam=_sendParams.get_tuple(),
            _fee=TxArgs(
                nativeFee=bridge_fee_wei,
                lzTokenFee=0
            ).get_tuple(),
            _refundAddress=self_address
        )

        tx_params = TxParams(
            to=bridge_contract.address,
            data=bridge_contract.encodeABI(
                'send',
                args=tx_args.get_tuple()
            ),
            value=bridge_fee_wei
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

    async def _quote_layer_zero_fee(
        self,
        router_contract: Web3ContractType,
        dst_chain_id: int,
        dst_fee: TokenAmount | None = None
    ) -> tuple[int, TxArgs]:
        lz_tx_params = TxArgs(
            dstGasForCall=0,
            dstNativeAmount=dst_fee.Wei if dst_fee else 0,
            dstNativeAddr=(
                self.client.account.address
                if dst_fee
                else TokenContractData.ZERO_ADDRESS
            )
        )

        fee_wei = await router_contract.functions.quoteLayerZeroFee(
            dst_chain_id,
            1,
            self.client.account.address,
            '0x',
            lz_tx_params.get_list()
        ).call()

        return fee_wei, lz_tx_params

    async def _quote_send_fee(
        self,
        router_contract: Web3ContractType,
        bridge_proposal: OperationProposal,
        adapter_params: str,
        dst_chain_id: int,
    ) -> tuple[int, TxArgs]:
        fee_wei = await router_contract.functions.quoteSendFee(
            [
                HexUtils.to_cut_hex_prefix_and_zfill(
                    self.client.account.address),
                bridge_proposal.amount_from.Wei,
                bridge_proposal.min_amount_to.Wei,
                dst_chain_id,
            ],
            adapter_params,
            False,
            '0x'
        ).call()

        return fee_wei


# region Random function
class Stargate(EvmTask):
    async def bridge(self) -> bool:
        settings = StargateSettings()
        bridge_data = get_stargate_routes()

        random_networks = list(bridge_data)
        random.shuffle(random_networks)

        self.client.custom_logger.log_message(
            status=LogStatus.INFO,
            message='Started to search enough balance for bridge'
        )

        for network_name in random_networks:
            client = EvmClient(
                account_id=self.client.account_id,
                private_key=self.client.account._private_key,
                network=Networks.get_network(network_name),
                proxy=self.client.proxy
            )

            (operation_info, dst_data) = await RandomChoiceHelper.get_partial_operation_info_and_dst_data(
                op_data=bridge_data,
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
        operation_info.to_network = Networks.get_network(random_dst_data[0])
        operation_info.to_token_name = random_dst_data[1]
        stargate = StargateImplementation(client)

        if settings.bridge_type['v1']:
            action = stargate.bridge_v1(operation_info,
                                        settings.bridge.max_fee_in_usd)
        else:
            v2_options = settings.bridge_type['v2']
            economy_option = BridgeType.Economy
            fast_option = BridgeType.Fast

            if (
                v2_options['fast']
                and v2_options['economy']
                and random_dst_data[2] == economy_option
            ):
                bridge_type = random.choice([economy_option, fast_option])
            elif v2_options['economy']:
                bridge_type = random_dst_data[2]
            elif v2_options['fast']:
                bridge_type = fast_option

            action = stargate.bridge_v2(operation_info, bridge_type)

        return await action
# endregion Random function
