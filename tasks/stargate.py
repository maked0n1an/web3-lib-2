import random
from typing import Tuple

from eth_abi import abi
from eth_typing import HexStr
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from data.config import MODULES_SETTINGS_FILE_PATH
from libs.async_eth_lib.architecture.client import EvmClient
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.data.token_contracts import ContractsFactory, TokenContractData
from libs.async_eth_lib.models.bridge import NetworkData, NetworkDataFetcher, TokenBridgeInfo
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.operation import OperationInfo, OperationProposal
from libs.async_eth_lib.models.others import LogStatus, ParamsTypes, TokenAmount, TokenSymbol
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.evm_task import EvmTask
from tasks._common.utils import RandomChoiceHelper, StandardSettings, Utils
from tasks.config import get_stargate_routes_v1


# region Settings
class StargateSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)
        
        self.bridge_type: dict[str, bool] = settings['stargate']['bridge_type']
        self.bridge = StandardSettings(
            settings=settings,
            module_name='stargate',
            action_name='bridge'
        )
        
        self.slippage_and_gas: float = settings['stargate']['slippage_and_gas']
# endregion Settings


# region Contracts
class StargateContractsV1:
    STARGATE_ROUTER_ABI = ('data', 'abis', 'stargate', 'router_abi.json')
    STARGATE_ROUTER_ETH_ABI = ('data', 'abis', 'stargate', 'router_eth_abi.json')
    STARGATE_STG_ABI = ('data', 'abis', 'stargate', 'stg_abi.json')
    STARGATE_BRIDGE_RECOLOR = ('data', 'abis', 'stargate', 'bridge_recolor.json')
    STARGATE_MESSAGING_V1_ABI = ('data', 'abis', 'stargate', 'msg_abi.json')

    ARBITRUM_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Arbitrum USDC)',
        address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
        abi_path=STARGATE_ROUTER_ABI
    )

    ARBITRUM_ETH = RawContract(
        title='Stargate Finance: Router (Arbitrum ETH)',
        address='0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40',
        abi_path=STARGATE_ROUTER_ETH_ABI
    )

    ARBITRUM_USDV = ContractsFactory.get_contract(
        network_name=Networks.Arbitrum.name,
        token_symbol=TokenSymbol.USDV
    )

    ARBITRUM_USDV_BRIDGE_RECOLOR_NOT_WORKING = RawContract(
        title='BridgeRecolor (Arbitrum)',
        address='0xAb43a615526e3e15B63e5812f74a0A1B86E9965E',
        abi_path=STARGATE_BRIDGE_RECOLOR
    )

    ARBITRUM_STG = RawContract(
        title='Stargate Finance: (Arbitrum STG)',
        address='0x6694340fc020c5e6b96567843da2df01b2ce1eb6',
        abi_path=STARGATE_ROUTER_ETH_ABI
    )

    AVALANCHE_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Avalanche Universal)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi_path=STARGATE_ROUTER_ABI
    )

    AVALANCHE_USDT = RawContract(
        title='Stargate Finance: Router (Avalanche USDT)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi_path=STARGATE_ROUTER_ABI
    )

    AVALANCHE_STG = RawContract(
        title='Stargate Finance (Avalanche STG)',
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
        abi_path=STARGATE_STG_ABI
    )

    AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING = RawContract(
        title='BridgeRecolor (AVAX-C)',
        address='0x292dD933180412923ee47fA73bBF407B6d776B4C',
        abi_path=STARGATE_BRIDGE_RECOLOR
    )

    AVALANCHE_USDV = ContractsFactory.get_contract(
        network_name=Networks.Avalanche.name,
        token_symbol=TokenSymbol.USDV
    )

    BSC_USDT = RawContract(
        title='Stargate Finance: Router (BSC USDT)',
        address='0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
        abi_path=STARGATE_ROUTER_ABI
    )

    BSC_BUSD = RawContract(
        title='Stargate Finance: Router (BSC BUSD)',
        address='0xB16f5A073d72cB0CF13824d65aA212a0e5c17D63',
        abi_path=STARGATE_ROUTER_ABI
    )

    BSC_STG = RawContract(
        title='Stargate Finance: (STG Token)',
        address='0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
        abi_path=STARGATE_STG_ABI
    )

    BSC_USDV_BRIDGE_RECOLOR = RawContract(
        title='BridgeRecolor (BSC)',
        address='0x5B1d0467BED2e8Bd67c16cE8bCB22a195ae76870',
        abi_path=STARGATE_BRIDGE_RECOLOR
    )

    BSC_USDV = ContractsFactory.get_contract(
        network_name=Networks.BSC.name,
        token_symbol=TokenSymbol.USDV
    )

    FANTOM_USDC = RawContract(
        title='Stargate Finance: Router (Fantom USDC)',
        address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
        abi_path=STARGATE_ROUTER_ABI
    )

    OPTIMISM_ETH = RawContract(
        title='Stargate Finance: ETH Router (Optimism)',
        address='0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b',
        abi_path=STARGATE_ROUTER_ETH_ABI
    )

    OPTIMISM_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Optimism USDC)',
        address='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
        abi_path=STARGATE_ROUTER_ABI
    )

    OPTIMISM_USDV_BRIDGE_RECOLOR = RawContract(
        title='BridgeRecolor (Optimism)',
        address='0x31691Fd2Cf50c777943b213836C342327f0DAB9b',
        abi_path=STARGATE_BRIDGE_RECOLOR
    )

    OPTIMISM_USDV = ContractsFactory.get_contract(
        network_name=Networks.Optimism.name,
        token_symbol=TokenSymbol.USDV
    )

    POLYGON_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Polygon Universal)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi_path=STARGATE_ROUTER_ABI
    )
    POLYGON_STG = RawContract(
        title='Stargate Finance: STG Token',
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
        abi_path=STARGATE_STG_ABI
    )
    POLYGON_USDV_BRIDGE_RECOLOR_NOT_WORKING = RawContract(
        title='BridgeRecolor (Polygon)',
        address='0xAb43a615526e3e15B63e5812f74a0A1B86E9965E',
        abi_path=STARGATE_BRIDGE_RECOLOR
    )

    POLYGON_USDV = ContractsFactory.get_contract(
        network_name=Networks.Polygon.name,
        token_symbol=TokenSymbol.USDV
    )


class StargateContractsV2:
    STARGATE_V2_ABI = ('data', 'abis', 'stargate', 'router_abi_v2.json')

    ARBITRUM_ETH = RawContract(
        title='StargatePoolNative_ETH (ARB)',
        address='0xA45B5130f36CDcA45667738e2a258AB09f4A5f7F',
        abi_path=STARGATE_V2_ABI
    )

    ARBITRUM_USDT = RawContract(
        title='StargatePoolMigratable_USDT (ARB)',
        address='0xce8cca271ebc0533920c83d39f417ed6a0abb7d0',
        abi_path=STARGATE_V2_ABI
    )
    
    BSC_USDT = RawContract(
        title='StargatePoolNative_USDT (BSC)',
        address='0x138eb30f73bc423c6455c53df6d89cb01d9ebc63',
        abi_path=STARGATE_V2_ABI
    )

    OPTIMISM_ETH = RawContract(
        title='StargatePoolNative_ETH (OP)',
        address='0xe8CDF27AcD73a434D661C84887215F7598e7d0d3',
        abi_path=STARGATE_V2_ABI
    )

    OPTIMISM_USDT = RawContract(
        title='StargatePoolMigratable_USDT (OP)',
        address='0x19cfce47ed54a88614648dc3f19a5980097007dd',
        abi_path=STARGATE_V2_ABI
    )
    
    POLYGON_USDT = RawContract(
        title='StargatePoolMigratable_USDT (POL)',
        address='0xd47b03ee6d86Cf251ee7860FB2ACf9f91B9fD4d7',
        abi_path=STARGATE_V2_ABI
    )
# endregion Stargate contracts


# region Supported networks
class StargateDataV1(NetworkDataFetcher):
    SPECIAL_COINS = [
        TokenSymbol.USDV
    ]

    NETWORKS_DATA = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.ARBITRUM_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.ARBITRUM_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.ARBITRUM_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.ARBITRUM_ETH,
                    pool_id=13
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.BSC_STG
                ),
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.ARBITRUM_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.ARBITRUM_USDV
                )
            }
        ),
        Networks.Avalanche.name: NetworkData(
            chain_id=106,
            bridge_dict={
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.AVALANCHE_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.AVALANCHE_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.AVALANCHE_STG
                ),
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                # TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.AVALANCHE_USDV
                )
            }
        ),
        Networks.BSC.name: NetworkData(
            chain_id=102,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.BSC_USDT,
                    pool_id=2
                ),
                TokenSymbol.BUSD: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.BSC_BUSD,
                    pool_id=5
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.BSC_STG
                ),
                TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.BSC_USDV_BRIDGE_RECOLOR
                ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.BSC_USDV
                ),
            }
        ),
        Networks.Fantom.name: NetworkData(
            chain_id=112,
            bridge_dict={
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.FANTOM_USDC,
                    pool_id=21
                )
            }
        ),
        Networks.Optimism.name: NetworkData(
            chain_id=111,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.OPTIMISM_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.OPTIMISM_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.OPTIMISM_ETH,
                    pool_id=13
                ),
                TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.OPTIMISM_USDV_BRIDGE_RECOLOR,
                ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.OPTIMISM_USDV
                )
            }
        ),
        Networks.Polygon.name: NetworkData(
            chain_id=109,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.POLYGON_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.POLYGON_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.POLYGON_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.POLYGON_STG
                ),
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.POLYGON_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                # TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.POLYGON_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContractsV1.POLYGON_USDV
                )
            }
        )
    }


class StargateDataV2(NetworkDataFetcher):
    NETWORKS_DATA = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=30110,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV2.ARBITRUM_USDT
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContractsV2.ARBITRUM_ETH
                )
            }
        ),
        Networks.Optimism.name: NetworkData(
            chain_id=30111,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV2.OPTIMISM_USDT
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContractsV2.OPTIMISM_ETH
                )
            }
        ),
        Networks.BSC.name: NetworkData(
            chain_id=30102,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV2.BSC_USDT
                )
            }
        ),
        Networks.Polygon.name: NetworkData(
            chain_id=30109,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContractsV2.POLYGON_USDT
                )
            }
        )
    }
    # Bridge types (https://stargateprotocol.gitbook.io/stargate/v/v2-developer-docs/integrate-with-stargate/how-to-swap)
    BUS: str = '0x01'
    TAXI: str = '0x'

    @classmethod
    def get_bridge_type_name(cls, value: str) -> str:
        for attr, val in cls.__dict__.items():
            if value == val:
                return attr
        return 'Unknown'
# endregion Stargate supported networks


# region Implementation
class StargateImplementation(EvmTask, Utils):
    @property
    def token_path(self) -> str:
        return self.__token_path

    @token_path.setter
    def token_path(self, crosschain_swap_info: OperationInfo):
        self.__token_path = crosschain_swap_info.from_token_name
        if crosschain_swap_info.to_token_name in StargateDataV1.SPECIAL_COINS:
            self.__token_path += crosschain_swap_info.to_token_name
            
    def __init__(self, client: EvmClient):
        super().__init__(client)
        self.__token_path = None

    async def bridge_v1(
        self,
        bridge_info: OperationInfo,
        max_fee: float = 0.7,
        dst_fee: float | TokenAmount | None = None
    ) -> bool:
        is_result = False
        check_message = self.validate_inputs(
            first_arg=self.client.network.name,
            second_arg=bridge_info.to_network.name,
            param_type='networks',
            function='bridge'
        )
        if check_message:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return is_result
        
        self.token_path = bridge_info
        dst_network_name_upper = bridge_info.to_network.name

        src_bridge_info = StargateDataV1.get_token_bridge_info(
            network_name=self.client.network.name,
            token_symbol=self.token_path
        )
        bridge_info = self._config_slippage_and_gas_price(
            bridge_info
        )
        bridge_proposal = await self.compute_source_token_amount(bridge_info)
        bridge_proposal.to_token = ContractsFactory.get_contract(
            network_name=bridge_info.to_network.name,
            token_symbol=bridge_info.to_token_name
        )
        bridge_proposal = await self.compute_min_destination_amount(
            operation_proposal=bridge_proposal,
            min_to_amount=bridge_proposal.amount_from.Wei,
            operation_info=bridge_info,
            is_to_token_price_wei=True
        )

        if dst_fee and isinstance(dst_fee, float):
            dst_network = Networks.get_network(
                network_name=dst_network_name_upper
            )
            dst_fee = TokenAmount(
                amount=dst_fee,
                decimals=dst_network.decimals
            )
            
        tx_params, bridge_info, bridge_proposal = await self._get_data_for_crosschain_swap(
            bridge_info=bridge_info,
            bridge_proposal=bridge_proposal,
            token_bridge_info=src_bridge_info,
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

        token_price = await self.get_binance_price(
            first_token=self.client.network.coin_symbol
        )
        network_fee = float(value.Ether) * token_price

        dst_native_amount_price = 0
        if dst_fee:
            dst_native_token_price = await self.get_binance_price(
                dst_network.coin_symbol
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
                token_contract=bridge_proposal.from_token,
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
                await sleep(20, 50)
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
                f'{bridge_info.to_token_name} in {dst_network_name_upper}: '
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
        bridge_type: str = StargateDataV2.BUS,
        max_fee: float = 0.7,
    ) -> bool:
        is_result = False
        self.token_path = bridge_info
        
        bridge_info = self._config_slippage_and_gas_price(
            bridge_info
        )
        bridge_proposal = await self.compute_source_token_amount(bridge_info)
        bridge_proposal = await self.compute_min_destination_amount(
            operation_proposal=bridge_proposal,
            min_to_amount=bridge_proposal.amount_from.Wei,
            operation_info=bridge_info,
            is_to_token_price_wei=True
        )
        
        dst_chain_id = StargateDataV2.get_chain_id(
            network_name=bridge_info.to_network.name
        )
        bridge_details = StargateDataV2.get_token_bridge_info(
            network_name=self.client.network.name,
            token_symbol=bridge_info.from_token_name
        )
        
        contract = self.client.contract.get_evm_contract_from_raw(
            bridge_details.bridge_contract
        )
        
        _sendParams = TxArgs(
            dstEid=dst_chain_id,
            to=self.zfill_hex_value(self.client.account.address),
            amountLd=bridge_proposal.amount_from.Wei,
            minAmountLd=bridge_proposal.min_amount_to.Wei,
            extraOptions='0x',
            composeMsg='0x',
            oftCmd=bridge_type
        )
        
        bridge_fee = await self._quote_send_v2(
            web3_contract=contract,
            send_params=_sendParams
        )
        
        tx_args = TxArgs(
            _sendParam=_sendParams.get_tuple(),
            _fee=TxArgs(
                nativeFee=bridge_fee.Wei,
                lzTokenFee=0
            ).get_tuple(),
            _refundAddress=self.client.account.address
        )
        
        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                'send', args=tx_args.get_tuple()
            ),
            value=bridge_fee.Wei
        )
        
        if not await self._check_for_enough_balance(bridge_fee):
            return is_result
        
        token_price = await self.get_binance_price(
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
                token_contract=bridge_proposal.from_token,
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
                await sleep(8, 30)
        else:
            tx_params['value'] += bridge_proposal.amount_from.Wei
        
        try:
            tx_params = self.set_all_gas_params(bridge_info, tx_params) 
            
            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt(self.client.w3)
            
            rounded_amount_from = round(bridge_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(bridge_proposal.min_amount_to.Ether, 5)
            bridge_type = StargateDataV2.get_bridge_type_name(bridge_type)
            is_result = receipt['status']
            
            if is_result:
                status = LogStatus.BRIDGED
                message = f'V2 \'{bridge_type}\' '
            else:
                status = LogStatus.FAILED
                message = f'Bridge V2 \'{bridge_type}\' '

            message += (
                f'{rounded_amount_from} {bridge_info.from_token_name} '
                f'from {self.__src_network_name} -> {rounded_amount_to} '
                f'{bridge_info.to_token_name} in {dst_network_name}: '
                f'https://layerzeroscan.com/tx/{tx.hash.hex()}'
            )
        except web3_exceptions.ContractCustomError as e:
            message = 'V2: Try to make slippage more'
            status = LogStatus.ERROR
        except Exception as e:
            if 'insufficient funds for gas + value' in str(e):
                message = 'Insufficient funds for gas + value'

            else:
                message = str(e)
                
            status = LogStatus.ERROR
                
        self.client.custom_logger.log_message(status, message)

        return is_result

    def _config_slippage_and_gas_price(
        self,
        bridge_info: OperationInfo
    ) -> OperationInfo:
        settings = StargateSettings()

        if self.token_path not in settings.slippage_and_gas:
            slip_and_gas_dict = settings.slippage_and_gas['default']
        else:
            slip_and_gas_dict = settings.slippage_and_gas[self.token_path]

        slippage = settings.bridge.init_from_to(
            section=slip_and_gas_dict,
            key='slippage',
            lower_bound='from',
            upper_bound='to'
        )

        bridge_info.slippage = round(random.uniform(slippage.from_, slippage.to_), 1)
        gas_prices = slip_and_gas_dict.pop('gas_prices', None)

        if gas_prices and self.client.network.name in gas_prices:
            bridge_info.gas_price = (
               gas_prices[self.client.network.name]
            )

        return bridge_info

    async def _get_data_for_crosschain_swap(
        self,
        bridge_info: OperationInfo,
        bridge_proposal: OperationProposal,
        token_bridge_info: TokenBridgeInfo,
        dst_fee: TokenAmount | None = None
    ) -> Tuple[TxParams, OperationInfo, OperationProposal]:
        if bridge_info.to_token_name in StargateDataV1.SPECIAL_COINS:
            dst_chain_id = StargateDataV1.get_chain_id(
                network_name=bridge_info.to_network.name
            )
        else:
            dst_chain_id, dst_pool_id = StargateDataV1.get_chain_id_and_pool_id(
                network_name=bridge_info.to_network.name,
                token_symbol=bridge_info.to_token_name
            )

        l0_multiplier_fee = 1.06
        address = self.client.account.address
        router_contract = self.client.contract.get_evm_contract_from_raw(
            token_bridge_info.bridge_contract
        )
        tx_params = TxParams(to=router_contract.address)
        

        if bridge_info.from_token_name == TokenSymbol.ETH:
            call_address = (
                await router_contract.functions.stargateRouter().call()
            )
            call_contract = self.client.contract.get_evm_contract_from_raw(
                address=call_address,
                abi_or_path=StargateContractsV1.STARGATE_ROUTER_ABI
            )

            lz_tx_params = TxArgs(
                dstGasForCall=0,
                dstNativeAmount=0,
                dstNativeAddr=self.client.account.address
            )
            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _refundAddress=address,
                _toAddress=address,
                _amountLD=bridge_proposal.amount_from.Wei,
                _minAmountLd=bridge_proposal.min_amount_to.Wei,
            )

            tx_params['data'] = router_contract.encodeABI(
                'swapETH', args=tx_args.get_tuple()
            )

            fee = await self._quote_layer_zero_fee(
                router_contract=call_contract,
                dst_chain_id=dst_chain_id,
                lz_tx_params=lz_tx_params,
            )

        elif (
            bridge_info.from_token_name == TokenSymbol.USDV
            and bridge_info.to_token_name == TokenSymbol.USDV
        ):
            msg_contract_address = await router_contract.functions.getRole(3).call()
            msg_contract = self.client.contract.get_evm_contract(
                address=msg_contract_address,
                abi_or_path=StargateContractsV1.STARGATE_MESSAGING_V1_ABI
            )

            min_gas_limit = await msg_contract.functions.minDstGasLookup(
                dst_chain_id,
                1
            ).call()

            adapter_params = abi.encode(
                ["uint16", "uint64"], [1, min_gas_limit])
            adapter_params = self.client.w3.to_hex(
                adapter_params[30:])

            fee = await self._quote_send_fee(
                router_contract=router_contract,
                bridge_proposal=bridge_proposal,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )

            tx_args = TxArgs(
                _param=TxArgs(
                    to=self.to_cut_hex_prefix_and_zfill(address),
                    amountLD=bridge_proposal.amount_from.Wei,
                    minAmountLD=bridge_proposal.min_amount_to.Wei,
                    dstEid=dst_chain_id
                ).get_tuple(),
                _extraOptions=adapter_params,
                _msgFee=TxArgs(
                    nativeFee=int(fee.Wei * l0_multiplier_fee),
                    lzTokenFee=0
                ).get_tuple(),
                _refundAddress=address,
                _composeMsg='0x'
            )

            tx_params['data'] = router_contract.encodeABI(
                'send', args=tx_args.get_tuple()
            )

        elif (
            bridge_info.from_token_name != TokenSymbol.USDV
            and bridge_info.to_token_name == TokenSymbol.USDV
        ):
            lz_tx_params = TxArgs(
                lvl=1,
                limit=170000
            )
            color = await router_contract.functions.color().call()
            adapter_params = abi.encode(
                ["uint16", "uint64"], lz_tx_params.get_list()
            )
            adapter_params = self.client.w3.to_hex(
                adapter_params[30:])

            usdv_contract = self.client.contract.get_evm_contract_from_raw(
                bridge_proposal.to_token
            )

            fee = await self._quote_send_fee(
                router_contract=usdv_contract,
                bridge_proposal=bridge_proposal,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )

            tx_args = TxArgs(
                _swapParam=TxArgs(
                    _fromToken=bridge_proposal.from_token.address,
                    _fromTokenAmount=bridge_proposal.amount_from.Wei,
                    _minUSDVOut=bridge_proposal.min_amount_to.Wei
                ).get_tuple(),
                _color=color,
                _param=TxArgs(
                    to=self.to_cut_hex_prefix_and_zfill(address),
                    amountLD=bridge_proposal.amount_from.Wei,
                    minAmountLD=bridge_proposal.min_amount_to.Wei,
                    dstEid=dst_chain_id
                ).get_tuple(),
                _extraOptions=adapter_params,
                _msgFee=TxArgs(
                    nativeFee=int(fee.Wei * l0_multiplier_fee),
                    lzTokenFee=0
                ).get_tuple(),
                _refundAddress=address,
                _composeMsg='0x'
            )

            data = router_contract.encodeABI(
                'swapRecolorSend', args=tx_args.get_tuple()
            )

            tx_params['data'] = data

        elif bridge_info.from_token_name == TokenSymbol.STG:
            lz_tx_params = TxArgs(
                lvl=1,
                limit=85000
            )
            adapter_params = abi.encode(
                ["uint16", "uint64"], lz_tx_params.get_list()
            )
            adapter_params = self.client.w3.to_hex(
                adapter_params[30:])

            fee = await self._estimate_send_tokens_fee(
                stg_contract=router_contract,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )

            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _to=address,
                _qty=bridge_proposal.amount_from.Wei,
                zroPaymentAddress=TokenContractData.ZERO_ADDRESS,
                adapterParam=adapter_params
            )

            tx_params['data'] = router_contract.encodeABI(
                'sendTokens', args=tx_args.get_tuple()
            )

        else:
            lz_tx_params = TxArgs(
                dstGasForCall=0,
                dstNativeAmount=dst_fee.Wei if dst_fee else 0,
                dstNativeAddr=(
                    address
                    if dst_fee
                    else TokenContractData.ZERO_ADDRESS
                )
            )

            fee = await self._quote_layer_zero_fee(
                router_contract=router_contract,
                dst_chain_id=dst_chain_id,
                lz_tx_params=lz_tx_params,
            )

            tx_args = TxArgs(
                _dstChainId=dst_chain_id,
                _srcPoolId=token_bridge_info.pool_id,
                _dstPoolId=dst_pool_id,
                _refundAddress=address,
                _amountLD=bridge_proposal.amount_from.Wei,
                _minAmountLd=bridge_proposal.min_amount_to.Wei,
                _lzTxParams=lz_tx_params.get_tuple(),
                _to=address,
                _payload='0x'
            )

            tx_params['data'] = router_contract.encodeABI(
                'swap', args=tx_args.get_tuple()
            )

        tx_params['value'] = int(fee.Wei * l0_multiplier_fee)

        return tx_params, bridge_info, bridge_proposal
    
    async def _check_for_enough_balance(
        self,
        fee_amount: TokenAmount
    ) -> bool:
        native_balance = await self.client.contract.get_balance()
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


    async def _estimate_send_tokens_fee(
        self,
        stg_contract: ParamsTypes.Web3Contract,
        dst_chain_id: int,
        adapter_params: str | HexStr,
    ) -> TokenAmount:
        result = await stg_contract.functions.estimateSendTokensFee(
            dst_chain_id,
            False,
            adapter_params
        ).call()

        return TokenAmount(amount=result[0], wei=True)

    async def _quote_layer_zero_fee(
        self,
        router_contract: ParamsTypes.Web3Contract,
        dst_chain_id: int,
        lz_tx_params: TxArgs,
    ) -> TokenAmount:
        result = await router_contract.functions.quoteLayerZeroFee(
            dst_chain_id,
            1,
            self.client.account.address,
            '0x',
            lz_tx_params.get_list()
        ).call()

        return TokenAmount(amount=result[0], wei=True)

    async def _quote_send_fee(
        self,
        router_contract: ParamsTypes.Web3Contract,
        bridge_proposal: OperationProposal,
        dst_chain_id: int,
        adapter_params: str,
        use_lz_token: bool = False,
    ) -> TokenAmount:
        address = self.to_cut_hex_prefix_and_zfill(
            self.client.account.address
        )

        result = await router_contract.functions.quoteSendFee(
            [
                address,
                bridge_proposal.amount_from.Wei,
                bridge_proposal.min_amount_to.Wei,
                dst_chain_id
            ],
            adapter_params,
            use_lz_token,
            "0x"
        ).call()

        return TokenAmount(
            amount=result[0],
            decimals=self.client.network.decimals,
            wei=True
        )
        
    async def _quote_send_v2(
        self,
        web3_contract: ParamsTypes.Web3Contract,
        send_params: TxArgs,
    ) -> TokenAmount:
        bridge_fee = await web3_contract.functions.quoteSend(
            send_params.get_tuple(), False
        ).call()
        
        fee_amount = TokenAmount(
            amount=bridge_fee[0],
            wei=True
        )
        
        return fee_amount
# endregion


# region Random function
class Stargate(EvmTask):
    async def bridge(self) -> bool:
        settings = StargateSettings()
        bridge_data = get_stargate_routes_v1()

        random_networks = list(bridge_data)
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
                op_name='bridge',
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
        operation_info.to_network = random_dst_data[0]
        operation_info.to_token_name = random_dst_data[1]
        stargate = StargateImplementation(client)
        
        if settings.bridge_type['v1']:
            action = stargate.bridge_v1(operation_info, settings.bridge.max_fee_in_usd)
        else:
            v2_options = settings.bridge_type['v2']
            bus_option = StargateDataV2.BUS
            taxi_option = StargateDataV2.TAXI    
                
            if v2_options['bus'] and v2_options['taxi']:
                bridge_type = random.choice([bus_option, taxi_option])
            elif v2_options['bus']:
                bridge_type = bus_option
            elif v2_options['taxi']:
                bridge_type = taxi_option
            else:
                raise ValueError("Invalid Stargate bridge type configuration")
            
            action = stargate.bridge_v2(operation_info, bridge_type=bridge_type)
        
        return await action
# endregion Random function
