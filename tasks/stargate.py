import random
from typing import Tuple

import web3.exceptions as web3_exceptions
from eth_abi import abi
from eth_typing import HexStr
from web3.types import TxParams

from data.config import MODULES_SETTINGS_FILE_PATH
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.data.token_contracts import ContractsFactory, TokenContractData
from libs.async_eth_lib.models.bridge import NetworkData, NetworkDataFetcher, TokenBridgeInfo
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, ParamsTypes, TokenAmount, TokenSymbol
from libs.async_eth_lib.models.swap import OperationInfo, SwapProposal
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from libs.pretty_utils.type_functions.dataclasses import FromTo
from tasks._common.utils import BaseTask
from tasks.config import get_stargate_routes


# region Settings
class StargateSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)['stargate']

        self.bridge_eth_amount: FromTo = FromTo(
            from_=settings['bridge_eth_amount']['from'],
            to_=settings['bridge_eth_amount']['to']
        )
        self.bridge_eth_amount_percent: FromTo = FromTo(
            from_=settings['bridge_eth_amount']['min_percent'],
            to_=settings['bridge_eth_amount']['max_percent']
        )
        self.bridge_stables_amount: FromTo = FromTo(
            from_=settings['bridge_stables_amount']['from'],
            to_=settings['bridge_stables_amount']['to']
        )
        self.bridge_stables_amount_percent: FromTo = FromTo(
            from_=settings['bridge_stables_amount']['min_percent'],
            to_=settings['bridge_stables_amount']['max_percent']
        )
        self.max_bridge_fee_usd: float = settings['max_bridge_fee_usd']


class StargateSlippageSettings():
    def __init__(self):
        self.slip_and_gas = (
            read_json(MODULES_SETTINGS_FILE_PATH)['stargate_settings']['slippage_and_gas']
        )
# endregion Settings


# region Contracts
class StargateContracts:
    STARGATE_ROUTER_ABI = read_json(
        path=('data', 'abis', 'stargate', 'router_abi.json')
    )

    STARGATE_ROUTER_ETH_ABI = read_json(
        path=('data', 'abis', 'stargate', 'router_eth_abi.json')
    )

    STARGATE_STG_ABI = read_json(
        path=('data', 'abis', 'stargate', 'stg_abi.json')
    )

    STARGATE_BRIDGE_RECOLOR = read_json(
        path=('data', 'abis', 'stargate', 'bridge_recolor.json')
    )
    STARGATE_MESSAGING_V1_ABI = read_json(
        path=('data', 'abis', 'stargate', 'msg_abi.json')
    )

    ARBITRUM_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Arbitrum USDC)',
        address='0x53bf833a5d6c4dda888f69c22c88c9f356a41614',
        abi=STARGATE_ROUTER_ABI
    )

    ARBITRUM_ETH = RawContract(
        title='Stargate Finance: Router (Arbitrum ETH)',
        address='0xbf22f0f184bCcbeA268dF387a49fF5238dD23E40',
        abi=STARGATE_ROUTER_ETH_ABI
    )

    ARBITRUM_USDV = ContractsFactory.get_contract(
        network_name=Networks.Arbitrum.name,
        token_symbol=TokenSymbol.USDV
    )

    ARBITRUM_USDV_BRIDGE_RECOLOR_NOT_WORKING = RawContract(
        title='BridgeRecolor (Arbitrum)',
        address='0xAb43a615526e3e15B63e5812f74a0A1B86E9965E',
        abi=STARGATE_BRIDGE_RECOLOR
    )

    ARBITRUM_STG = RawContract(
        title='Stargate Finance: (Arbitrum STG)',
        address='0x6694340fc020c5e6b96567843da2df01b2ce1eb6',
        abi=STARGATE_ROUTER_ETH_ABI
    )

    AVALANCHE_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Avalanche Universal)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ROUTER_ABI
    )

    AVALANCHE_USDT = RawContract(
        title='Stargate Finance: Router (Avalanche USDT)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ROUTER_ABI
    )

    AVALANCHE_STG = RawContract(
        title='Stargate Finance (Avalanche STG)',
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
        abi=STARGATE_STG_ABI
    )

    AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING = RawContract(
        title='BridgeRecolor (AVAX-C)',
        address='0x292dD933180412923ee47fA73bBF407B6d776B4C',
        abi=STARGATE_BRIDGE_RECOLOR
    )

    AVALANCHE_USDV = ContractsFactory.get_contract(
        network_name=Networks.Avalanche.name,
        token_symbol=TokenSymbol.USDV
    )

    BSC_USDT = RawContract(
        title='Stargate Finance: Router (BSC USDT)',
        address='0x4a364f8c717cAAD9A442737Eb7b8A55cc6cf18D8',
        abi=STARGATE_ROUTER_ABI
    )

    BSC_BUSD = RawContract(
        title='Stargate Finance: Router (BSC BUSD)',
        address='0xB16f5A073d72cB0CF13824d65aA212a0e5c17D63',
        abi=STARGATE_ROUTER_ABI
    )

    BSC_STG = RawContract(
        title='Stargate Finance: (STG Token)',
        address='0xB0D502E938ed5f4df2E681fE6E419ff29631d62b',
        abi=STARGATE_STG_ABI
    )

    BSC_USDV_BRIDGE_RECOLOR = RawContract(
        title='BridgeRecolor (BSC)',
        address='0x5B1d0467BED2e8Bd67c16cE8bCB22a195ae76870',
        abi=STARGATE_BRIDGE_RECOLOR
    )

    BSC_USDV = ContractsFactory.get_contract(
        network_name=Networks.BSC.name,
        token_symbol=TokenSymbol.USDV
    )

    FANTOM_USDC = RawContract(
        title='Stargate Finance: Router (Fantom USDC)',
        address='0xAf5191B0De278C7286d6C7CC6ab6BB8A73bA2Cd6',
        abi=STARGATE_ROUTER_ABI
    )

    OPTIMISM_ETH = RawContract(
        title='Stargate Finance: ETH Router (Optimism)',
        address='0xB49c4e680174E331CB0A7fF3Ab58afC9738d5F8b',
        abi=STARGATE_ROUTER_ETH_ABI
    )

    OPTIMISM_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Optimism USDC)',
        address='0xb0d502e938ed5f4df2e681fe6e419ff29631d62b',
        abi=STARGATE_ROUTER_ABI
    )

    OPTIMISM_USDV_BRIDGE_RECOLOR = RawContract(
        title='BridgeRecolor (Optimism)',
        address='0x31691Fd2Cf50c777943b213836C342327f0DAB9b',
        abi=STARGATE_BRIDGE_RECOLOR
    )

    OPTIMISM_USDV = ContractsFactory.get_contract(
        network_name=Networks.Optimism.name,
        token_symbol=TokenSymbol.USDV
    )

    POLYGON_UNIVERSAL = RawContract(
        title='Stargate Finance: Router (Polygon Universal)',
        address='0x45A01E4e04F14f7A4a6702c74187c5F6222033cd',
        abi=STARGATE_ROUTER_ABI
    )
    POLYGON_STG = RawContract(
        title='Stargate Finance: STG Token',
        address='0x2F6F07CDcf3588944Bf4C42aC74ff24bF56e7590',
        abi=STARGATE_STG_ABI
    )
    POLYGON_USDV_BRIDGE_RECOLOR_NOT_WORKING = RawContract(
        title='BridgeRecolor (Polygon)',
        address='0xAb43a615526e3e15B63e5812f74a0A1B86E9965E',
        abi=STARGATE_BRIDGE_RECOLOR
    )

    POLYGON_USDV = ContractsFactory.get_contract(
        network_name=Networks.Polygon.name,
        token_symbol=TokenSymbol.USDV
    )
# endregion Stargate contracts


# region Supported networks
class StargateData(NetworkDataFetcher):
    SPECIAL_COINS = [
        TokenSymbol.USDV
    ]

    NETWORKS_DATA = {
        Networks.Arbitrum.name: NetworkData(
            chain_id=110,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_ETH,
                    pool_id=13
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_STG
                ),
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.ARBITRUM_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.ARBITRUM_USDV
                )
            }
        ),
        Networks.Avalanche.name: NetworkData(
            chain_id=106,
            bridge_dict={
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_STG
                ),
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                # TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.AVALANCHE_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.AVALANCHE_USDV
                )
            }
        ),
        Networks.BSC.name: NetworkData(
            chain_id=102,
            bridge_dict={
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_USDT,
                    pool_id=2
                ),
                TokenSymbol.BUSD: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_BUSD,
                    pool_id=5
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_STG
                ),
                TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_USDV_BRIDGE_RECOLOR
                ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.BSC_USDV
                ),
            }
        ),
        Networks.Fantom.name: NetworkData(
            chain_id=112,
            bridge_dict={
                TokenSymbol.USDC: TokenBridgeInfo(
                    bridge_contract=StargateContracts.FANTOM_USDC,
                    pool_id=21
                )
            }
        ),
        Networks.Optimism.name: NetworkData(
            chain_id=111,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.ETH: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_ETH,
                    pool_id=13
                ),
                TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_USDV_BRIDGE_RECOLOR,
                ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.OPTIMISM_USDV
                )
            }
        ),
        Networks.Polygon.name: NetworkData(
            chain_id=109,
            bridge_dict={
                TokenSymbol.USDC_E: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=1
                ),
                TokenSymbol.USDT: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=2
                ),
                TokenSymbol.DAI: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_UNIVERSAL,
                    pool_id=3
                ),
                TokenSymbol.STG: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_STG
                ),
                # TokenSymbol.USDC_E + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.POLYGON_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                # TokenSymbol.USDT + TokenSymbol.USDV: TokenBridgeInfo(
                #     bridge_contract=StargateContracts.POLYGON_USDV_BRIDGE_RECOLOR_NOT_WORKING,
                # ),
                TokenSymbol.USDV + TokenSymbol.USDV: TokenBridgeInfo(
                    bridge_contract=StargateContracts.POLYGON_USDV
                )
            }
        )
    }
# endregion Stargate supported networks


# region Implementation
class StargateImplementation(BaseTask):
    @property
    def src_network_name(self):
        """The source network name"""
        return self._src_network_name
    
    @src_network_name.setter
    def src_network_name(self, value: str):
        self._src_network_name = value.upper()

    @property
    def token_path(self) -> str:
        return self._token_path
    
    @token_path.setter
    def token_path(self, crosschain_swap_info: OperationInfo):
        self._token_path = crosschain_swap_info.from_token_name
        if crosschain_swap_info.to_token_name in StargateData.SPECIAL_COINS:
            self._token_path += crosschain_swap_info.to_token_name

    async def bridge(
        self,
        bridge_info: OperationInfo,
        max_fee: float = 0.7,
        dst_fee: float | TokenAmount | None = None
    ) -> bool:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.network.name,
            second_arg=bridge_info.to_network.name,
            param_type='networks'
        )
        if check_message:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        
        self.src_network_name = self.client.network.name
        self.token_path = bridge_info
        dst_network_name = bridge_info.to_network.name.upper()

        src_bridge_info = StargateData.get_token_bridge_info(
            network_name=self.src_network_name,
            token_symbol=self.token_path
        )
        
        swap_proposal = await self.compute_source_token_amount(bridge_info)
        swap_proposal = await self.compute_min_destination_amount(
            swap_proposal=swap_proposal,
            min_to_amount=swap_proposal.amount_from.Wei,
            swap_info=bridge_info,
            is_to_token_price_wei=True
        )

        if dst_fee and isinstance(dst_fee, float):
            dst_network = Networks.get_network(
                network_name=dst_network_name
            )
            dst_fee = TokenAmount(
                amount=dst_fee,
                decimals=dst_network.decimals
            )
            
        tx_params, bridge_info, swap_proposal = await self.get_data_for_crosschain_swap(
            crosschain_swap_info=bridge_info,
            swap_proposal=swap_proposal,
            src_bridge_info=src_bridge_info,
            dst_fee=dst_fee
        )
        if 'value' not in tx_params:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Can not get value for ({self.src_network_name})'
                )
            )
            return False

        native_balance = await self.client.contract.get_balance()
        value = TokenAmount(
            amount=tx_params['value'],
            decimals=self.client.network.decimals,
            wei=True
        )

        if native_balance.Wei < value.Wei:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message=(
                    f'Too low balance: balance: '
                    f'balance - {round(native_balance.Ether, 5)}; '
                    f'value - {round(value.Ether, 5)}'
                )
            )

            return False

        token_price = await self.get_binance_ticker_price(
            first_token=self.client.network.coin_symbol
        )
        network_fee = float(value.Ether) * token_price

        dst_native_amount_price = 0
        if dst_fee:
            dst_native_token_price = await self.get_binance_ticker_price(
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

            return False

        if not swap_proposal.from_token.is_native_token:
            optional_tx_hash = await self.approve_interface(
                swap_info=bridge_info,
                token_contract=swap_proposal.from_token,
                tx_params=tx_params,
                amount=swap_proposal.amount_from,
            )

            if optional_tx_hash:
                self.client.custom_logger.log_message(
                    status=LogStatus.APPROVED,
                    message=(
                        f'{swap_proposal.from_token.title}'
                        f'{swap_proposal.amount_from.Ether}'
                    )
                )
                await sleep(20, 50)
        else:
            tx_params['value'] += swap_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                operation_info=bridge_info,
                tx_params=tx_params
            )
            
            tx = await self.client.contract.sign_and_send(tx_params)
                
            receipt = await tx.wait_for_tx_receipt(
                web3=self.client.w3,
                timeout=240
            )
            
            rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(swap_proposal.min_amount_to.Ether, 5)

            if receipt['status']:
                status = LogStatus.BRIDGED
                message = ''
            else:
                status = LogStatus.FAILED
                message = f'Bridge'

            message += (
                f'{rounded_amount_from} {bridge_info.from_token_name} '
                f'from {self.src_network_name} -> {rounded_amount_to} '
                f'{bridge_info.to_token_name} in {dst_network_name}: '
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

            if 'insufficient funds for gas + value' in error:
                message = 'Insufficient funds for gas + value'

            else:
                message = error
                
        self.client.custom_logger.log_message(status, message)

        return False

    def config_slippage_and_gas_price(
        self,
        swap_info: OperationInfo
    ) -> OperationInfo:
        settings = StargateSlippageSettings()

        if self.token_path not in settings.slip_and_gas:
            slip_and_gas_dict = settings.slip_and_gas['default']
        else:
            slip_and_gas_dict = settings.slip_and_gas[self.token_path]

        slippage: FromTo = FromTo(
            from_=slip_and_gas_dict['slippage']['from'] * 10,
            to_=slip_and_gas_dict['slippage']['to'] * 10
        )

        swap_info.slippage = random.randint(slippage.from_, slippage.to_)
        gas_prices = slip_and_gas_dict.pop('gas_prices', None)
        
        if gas_prices and self.src_network_name in gas_prices:
            swap_info.gas_price = (
                slip_and_gas_dict['gas_prices'][self.src_network_name]
            )

        return swap_info

    async def get_data_for_crosschain_swap(
        self,
        crosschain_swap_info: OperationInfo,
        swap_proposal: SwapProposal,
        src_bridge_info: TokenBridgeInfo,
        dst_fee: TokenAmount | None = None
    ) -> Tuple[TxParams, OperationInfo, SwapProposal]:
        if crosschain_swap_info.to_token_name in StargateData.SPECIAL_COINS:
            dst_chain_id = StargateData.get_chain_id(
                network_name=crosschain_swap_info.to_network.name
            )
        else:
            dst_chain_id, dst_pool_id = StargateData.get_chain_id_and_pool_id(
                network_name=crosschain_swap_info.to_network.name,
                token_symbol=crosschain_swap_info.to_token_name
            )

        l0_multiplier_fee = 1.06
        address = self.client.account.address
        router_contract = await self.client.contract.get(
            contract=src_bridge_info.bridge_contract
        )
        tx_params = TxParams(to=router_contract.address)

        crosschain_swap_info = self.config_slippage_and_gas_price(
            crosschain_swap_info
        )

        if crosschain_swap_info.from_token_name == TokenSymbol.ETH:
            router_call_address = (
                await router_contract.functions.stargateRouter().call()
            )
            router_call_contract = await self.client.contract.get(
                contract=router_call_address,
                abi=StargateContracts.STARGATE_ROUTER_ABI
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
                _amountLD=swap_proposal.amount_from.Wei,
                _minAmountLd=swap_proposal.min_amount_to.Wei,
            )

            tx_params['data'] = router_contract.encodeABI(
                'swapETH', args=tx_args.get_tuple()
            )

            fee = await self._quote_layer_zero_fee(
                router_contract=router_call_contract,
                dst_chain_id=dst_chain_id,
                lz_tx_params=lz_tx_params,
            )

        elif (
            crosschain_swap_info.from_token_name == TokenSymbol.USDV
            and crosschain_swap_info.to_token_name == TokenSymbol.USDV
        ):
            msg_contract_address = await router_contract.functions.getRole(3).call()
            msg_contract = await self.client.contract.get(
                contract=msg_contract_address,
                abi=StargateContracts.STARGATE_MESSAGING_V1_ABI
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
                swap_proposal=swap_proposal,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )

            tx_args = TxArgs(
                _param=TxArgs(
                    to=abi.encode(["address"], [address]),
                    amountLD=swap_proposal.amount_from.Wei,
                    minAmountLD=swap_proposal.min_amount_to.Wei,
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
            crosschain_swap_info.from_token_name != TokenSymbol.USDV
            and crosschain_swap_info.to_token_name == TokenSymbol.USDV
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

            usdv_contract = await self.client.contract.get(
                contract=swap_proposal.to_token
            )

            fee = await self._quote_send_fee(
                router_contract=usdv_contract,
                swap_proposal=swap_proposal,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )

            tx_args = TxArgs(
                _swapParam=TxArgs(
                    _fromToken=swap_proposal.from_token.address,
                    _fromTokenAmount=swap_proposal.amount_from.Wei,
                    _minUSDVOut=swap_proposal.min_amount_to.Wei
                ).get_tuple(),
                _color=color,
                _param=TxArgs(
                    to=abi.encode(['address'], [address]),
                    amountLD=swap_proposal.amount_from.Wei,
                    minAmountLD=swap_proposal.min_amount_to.Wei,
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

        elif crosschain_swap_info.from_token_name == TokenSymbol.STG:
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
                _qty=swap_proposal.amount_from.Wei,
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
                _srcPoolId=src_bridge_info.pool_id,
                _dstPoolId=dst_pool_id,
                _refundAddress=address,
                _amountLD=swap_proposal.amount_from.Wei,
                _minAmountLd=swap_proposal.min_amount_to.Wei,
                _lzTxParams=lz_tx_params.get_tuple(),
                _to=address,
                _payload='0x'
            )

            tx_params['data'] = router_contract.encodeABI(
                'swap', args=tx_args.get_tuple()
            )

        tx_params['value'] = int(fee.Wei * l0_multiplier_fee)

        return tx_params, crosschain_swap_info, swap_proposal

    async def _estimate_send_tokens_fee(
        self,
        stg_contract: ParamsTypes.Contract,
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
        router_contract: ParamsTypes.Contract,
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
        router_contract: ParamsTypes.Contract,
        swap_proposal: SwapProposal,
        dst_chain_id: int,
        adapter_params: str,
        use_lz_token: bool = False,
    ) -> TokenAmount:
        address = abi.encode(
            ["address"],
            [self.client.account.address]
        )

        result = await router_contract.functions.quoteSendFee(
            [
                address,
                swap_proposal.amount_from.Wei,
                swap_proposal.min_amount_to.Wei,
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
# endregion


# region Random function
class Stargate(BaseTask):
    async def bridge(
        self,
    ):
        settings = StargateSettings()
        src_bridge_data = get_stargate_routes()

        random_networks = list(src_bridge_data.keys())
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

            dst_data = None
            random_tokens = list(src_bridge_data[network].keys())
            random.shuffle(random_tokens)

            found_token_symbol, found_amount_from = None, 0

            for token_sym in random_tokens:
                token_contract = ContractsFactory.get_contract(
                    network.name, token_sym
                )
                if token_contract.is_native_token:
                    balance = await client.contract.get_balance()

                    if float(balance.Ether) < settings.bridge_eth_amount.from_:
                        continue

                    amount_from = settings.bridge_eth_amount.from_
                    amount_to = min(float(balance.Ether), settings.bridge_eth_amount.to_)
                    min_percent = settings.bridge_eth_amount_percent.from_
                    max_percent = settings.bridge_eth_amount_percent.to_
                else:
                    balance = await client.contract.get_balance(token_contract)

                    if float(balance.Ether) < settings.bridge_stables_amount.from_:
                        continue

                    amount_from = settings.bridge_stables_amount.from_
                    amount_to = min(float(balance.Ether), settings.bridge_stables_amount.to_)
                    min_percent = settings.bridge_stables_amount_percent.from_
                    max_percent = settings.bridge_stables_amount_percent.to_

                crosschain_swap_info = OperationInfo(
                    from_token_name=token_sym,
                    amount_from=amount_from,
                    amount_to=amount_to,
                    min_percent=min_percent,
                    max_percent=max_percent
                )
                client = client
                dst_data = src_bridge_data[network][token_sym]
                found_token_symbol = crosschain_swap_info.from_token_name
                found_amount_from = (
                    crosschain_swap_info.amount
                    if crosschain_swap_info.amount
                    else round(crosschain_swap_info.amount_by_percent * float(balance.Ether), 6)
                )

            if dst_data:
                self.client.custom_logger.log_message(
                    status=LogStatus.INFO,
                    message=(
                        f'Found {found_amount_from} '
                        f'{found_token_symbol} in {network.name.capitalize()}!'
                    )
                )
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
        crosschain_swap_info.to_network = random_dst_data[0]
        crosschain_swap_info.to_token_name = random_dst_data[1]
        stargate = StargateImplementation(client)

        return await stargate.bridge(crosschain_swap_info, settings.max_bridge_fee_usd)
# endregion Random function