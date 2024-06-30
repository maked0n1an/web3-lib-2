import random
from typing import Tuple, Union
from web3.types import TxParams

from data.config import STARGATE_SLIPPAGE_OPTIONS
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.data.token_contracts import ContractsFactory, TokenContractData
from libs.async_eth_lib.models.bridge import NetworkData, NetworkDataFetcher, TokenBridgeInfo
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, TokenAmount, TokenSymbol
from libs.async_eth_lib.models.swap import SwapInfo, SwapProposal
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.utils import BaseTask


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
        if self._src_network_name is None:
            self._src_network_name = (
                self.client.account_manager.network.name.upper()
            )
        return self._src_network_name
    
    @src_network_name.setter
    def src_network_name(self, value: str):
        self._src_network_name = value.upper()
    
    async def bridge(
        self,
        swap_info: SwapInfo,
        max_fee: float = 0.7,
        dst_fee: float | TokenAmount | None = None
    ) -> str:
        check_message = self.validate_swap_inputs(
            first_arg=self.client.account_manager.network.name,
            second_arg=swap_info.dst_network.name,
            param_type='networks'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        self.src_network_name = self.client.account_manager.network.name
        dst_network_name = swap_info.dst_network.name
        
        full_path = swap_info.src_token_name
        if swap_info.dst_token_name in StargateData.SPECIAL_COINS:
            full_path += swap_info.dst_token_name
            
        src_bridge_info = StargateData.get_token_bridge_info(
            network_name=self.src_network_name,
            token_symbol=full_path
        )

        swap_proposal = await self.compute_source_token_amount(swap_info)
        swap_proposal = await self.compute_min_destination_amount(
            swap_proposal=swap_proposal,
            min_to_amount=swap_proposal.amount_from.Ether,
            swap_info=swap_info,
        )
        
        if dst_fee and isinstance(dst_fee, float):
            dst_network = Networks.get_network(
                network_name=dst_network_name
            )
            dst_fee = TokenAmount(
                amount=dst_fee,
                decimals=dst_network.decimals
            )

        prepared_tx_params, swap_info, swap_proposal = await self.get_data_for_crosschain_swap(
            swap_info=swap_info,
            swap_proposal=swap_proposal,
            src_bridge_info=src_bridge_info,
            dst_fee=dst_fee
        )
        if not prepared_tx_params['value']:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, 
                message=(
                    f'Can not get value for ({self.src_network_name})'
                )
            )

            return False
        
        native_balance = await self.client.contract.get_balance()
        value = TokenAmount(
            amount=prepared_tx_params['value'],
            decimals=self.client.account_manager.network.decimals,
            wei=True
        )

        if native_balance.Wei < value.Wei:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, 
                message=(
                    f'Too low balance: balance: '
                    f'{native_balance.Ether}; value: {value.Ether}'
                )
            )

            return False

        token_price = await self.get_binance_ticker_price(
            first_token=self.client.account_manager.network.coin_symbol
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
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, 
                message=(
                    f'Too high fee for bridge: max. fee: '
                    f'{max_fee}; value: {value.Ether}'
                )
            )

            return False

        if not swap_proposal.from_token.is_native_token:
            hexed_tx_hash = await self.approve_interface(
                swap_info=swap_info,
                token_contract=swap_proposal.from_token,
                tx_params=prepared_tx_params,
                amount=swap_proposal.amount_from,
            )

            if hexed_tx_hash:
                self.client.account_manager.custom_logger.log_message(
                    status=LogStatus.APPROVED,
                    message=(
                        f'{swap_proposal.from_token.title}'
                        f'{swap_proposal.amount_from.Ether}'
                    )
                )
                await sleep(20, 50)
        else:
            prepared_tx_params['value'] += swap_proposal.amount_from.Wei

        tx_params = self.set_all_gas_params(
            swap_info=swap_info,
            tx_params=tx_params
        )

        tx = await self.client.contract.transaction.sign_and_send(
            prepared_tx_params
        )
        receipt = await tx.wait_for_tx_receipt(client=self.client, timeout=300)

        rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
        rounded_amount_to = round(swap_proposal.min_to_amount.Ether, 5)

        if receipt['status']:
            status = LogStatus.BRIDGED
            message = f''
        else:
            status = LogStatus.FAILED
            message = f'Failed bridge'

        message += (
            f'{rounded_amount_from} {swap_info.src_token_name} '
            f'from {self.src_network_name} -> {rounded_amount_to} '
            f'{swap_info.dst_token_name} in {dst_network_name}: '
            f'https://layerzeroscan.com/tx/{tx.hash.hex()}'
        )
        
        self.client.account_manager.custom_logger.log_message(status, message)
        
        return True

    def config_some_operations(
        self,
        swap_info: SwapInfo
    ) -> Union[SwapInfo, float]:
        slippages_and_gas_prices_dict = {
            TokenSymbol.ETH: {
                'default_slippage' : random.randint(3, 5) / 10
            },
            TokenSymbol.USDV + TokenSymbol.USDV: {
                'default_slippage': 0,
                'gas_prices': {
                    Networks.BSC: 1
                }
            },
            TokenSymbol.USDV: {
                'default_slippage': random.randint(1, 5) / 10,
                'gas_prices': {
                    Networks.BSC: 2.5
                }
            },
            TokenSymbol.STG: {
                'default_slippage': random.randint(1, 3) / 10,
                'gas_prices': {
                    Networks.BSC: 3
                }
            },
            'default': {
                'default_slippage': random.randint(3, 5) / 10,
                'gas_prices': {
                    Networks.BSC: 3
                }
            }
        }
        
        # if swap_info.src_token_name == TokenSymbol.ETH:
        #     slippage = random.randint(3, 5) / 10

        # elif (
        #     swap_info.src_token_name == TokenSymbol.USDV
        #     and swap_info.dst_token_name == TokenSymbol.USDV
        # ):
        #     slippage = 0

        #     match self.client.account_manager.network:
        #         case Networks.BSC:
        #             swap_info.gas_price = 1

        # elif (
        #     swap_info.src_token_name != TokenSymbol.USDV
        #     and swap_info.dst_token_name == TokenSymbol.USDV
        # ):
        #     slippage = random.randint(1, 5) / 10

        #     match self.client.account_manager.network:
        #         case Networks.BSC:
        #             swap_info.gas_price = 2.5

        # elif swap_info.src_token_name == TokenSymbol.STG:
        #     slippage = random.randint(1, 3) / 10

        #     match self.client.account_manager.network:
        #         case Networks.BSC:
        #             swap_info.gas_price = 3

        # else:
        #     slippage = random.randint(3, 5) / 10

        #     match self.client.account_manager.network:
        #         case Networks.BSC:
        #             swap_info.gas_price = 3

        # swap_info.slippage = (
        #     slippage
        #     if not swap_info.slippage or swap_info.slippage == 0.5
        #     else swap_info.slippage
        # )
        
        if swap_info.src_token_name not in STARGATE_SLIPPAGE_OPTIONS:
            slip_and_gas_dict = STARGATE_SLIPPAGE_OPTIONS['default']
        else:
            slip_and_gas_dict = STARGATE_SLIPPAGE_OPTIONS[swap_info.src_token_name]
        
        swap_info.slippage = slip_and_gas_dict['default_slippage']
        if self.src_network_name in slip_and_gas_dict['gas_prices']: 
            swap_info.gas_price = (
                slip_and_gas_dict['gas_prices'][self.src_network_name]
            )

        
        multiplier_of_value = 1.06

        return swap_info, multiplier_of_value

    def get_wait_time(self) -> int:
        match self.client.network.name:
            case Networks.Arbitrum.name:
                wait_time = (0.9 * 60, 2 * 60)
            case Networks.Avalanche.name:
                wait_time = (1.5 * 60, 2.5 * 60)
            case Networks.BSC.name:
                wait_time = (2 * 60, 2.5 * 60)
            case Networks.Optimism.name:
                wait_time = (1.5 * 60, 2.3 * 60)
            case Networks.Polygon.name:
                wait_time = (22 * 60, 24 * 60)

        return random.randint(int(wait_time[0]), int(wait_time[1]))

    async def get_data_for_crosschain_swap(
        self,
        swap_info: SwapInfo,
        swap_proposal: SwapProposal,
        src_bridge_info: TokenBridgeInfo,
        dst_fee: TokenAmount | None = None
    ) -> Tuple[TxParams, SwapInfo, SwapProposal]:
        if swap_info.dst_token_name in StargateData.SPECIAL_COINS:
            dst_chain_id = StargateData.get_chain_id(
                network_name=swap_info.dst_network.name
            )
        else:
            dst_chain_id, dst_pool_id = StargateData.get_chain_id_and_pool_id(
                network_name=swap_info.dst_network.name,
                token_symbol=swap_info.dst_token_name
            )

        multiplier = 1.0
        address = self.client.account.address
        router_contract = await self.client.contracts.get(
            contract_address=src_bridge_info.bridge_contract
        )
        tx_params = TxParams(to=router_contract.address)

        swap_info, multiplier = self.config_some_operations(swap_info)
        
        if swap_info.src_token_name == TokenSymbol.ETH:
            router_call_address = (
                await router_contract.functions.stargateRouter().call()
            )
            router_call_contract = await self.client.contracts.get(
                contract_address=router_call_address,
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
                _minAmountLd=swap_proposal.min_to_amount.Wei,
            )

            tx_params['data'] = router_contract.encodeABI(
                'swapETH', args=tx_args.tuple()
            )

            fee = await self._quote_layer_zero_fee(
                router_contract=router_call_contract,
                dst_chain_id=dst_chain_id,
                lz_tx_params=lz_tx_params,
            )

        elif (
            swap_info.src_token_name == TokenSymbol.USDV
            and swap_info.dst_token_name == TokenSymbol.USDV
        ):            
            msg_contract_address = await router_contract.functions.getRole(3).call()
            msg_contract = await self.client.contracts.get(
                contract_address=msg_contract_address,
                abi=StargateContracts.STARGATE_MESSAGING_V1_ABI
            )

            min_gas_limit = await msg_contract.functions.minDstGasLookup(
                dst_chain_id,
                1
            ).call()

            adapter_params = abi.encode(["uint16", "uint64"], [1, min_gas_limit])
            adapter_params = self.client.w3.to_hex(adapter_params[30:])

            fee = await self._quote_send_fee(
                router_contract=router_contract,
                swap_query=swap_proposal,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )

            tx_args = TxArgs(
                _param=TxArgs(
                    to=abi.encode(["address"], [address]),
                    amountLD=swap_proposal.amount_from.Wei,
                    minAmountLD=swap_proposal.min_to_amount.Wei,
                    dstEid=dst_chain_id
                ).tuple(),
                _extraOptions=adapter_params,
                _msgFee=TxArgs(
                    nativeFee=int(fee.Wei * multiplier),
                    lzTokenFee=0
                ).tuple(),
                _refundAddress=address,
                _composeMsg='0x'
            )

            tx_params['data'] = router_contract.encodeABI(
                'send', args=tx_args.tuple()
            )

        elif (
            swap_info.src_token_name != TokenSymbol.USDV
            and swap_info.dst_token_name == TokenSymbol.USDV
        ):            
            lz_tx_params = TxArgs(
                lvl=1,
                limit=170000
            )
            color = await router_contract.functions.color().call()
            adapter_params = abi.encode(
                ["uint16", "uint64"], lz_tx_params.list()
            )
            adapter_params = self.client.w3.to_hex(adapter_params[30:])

            usdv_contract = await self.client.contracts.get(
                contract_address=swap_proposal.to_token
            )

            fee = await self._quote_send_fee(
                router_contract=usdv_contract,
                swap_query=swap_proposal,
                dst_chain_id=dst_chain_id,
                adapter_params=adapter_params
            )

            tx_args = TxArgs(
                _swapParam=TxArgs(
                    _fromToken=swap_proposal.from_token.address,
                    _fromTokenAmount=swap_proposal.amount_from.Wei,
                    _minUSDVOut=swap_proposal.min_to_amount.Wei
                ).tuple(),
                _color=color,
                _param=TxArgs(
                    to=abi.encode(['address'], [address]),
                    amountLD=swap_proposal.amount_from.Wei,
                    minAmountLD=swap_proposal.min_to_amount.Wei,
                    dstEid=dst_chain_id
                ).tuple(),
                _extraOptions=adapter_params,
                _msgFee=TxArgs(
                    nativeFee=int(fee.Wei * multiplier),
                    lzTokenFee=0
                ).tuple(),
                _refundAddress=address,
                _composeMsg='0x'
            )

            data = router_contract.encodeABI(
                'swapRecolorSend', args=tx_args.tuple()
            )

            tx_params['data'] = data

        elif swap_info.src_token_name == TokenSymbol.STG:
            lz_tx_params = TxArgs(
                lvl=1,
                limit=85000
            )
            adapter_params = abi.encode(
                ["uint16", "uint64"], lz_tx_params.list()
            )
            adapter_params = self.client.w3.to_hex(adapter_params[30:])

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
                'sendTokens', args=tx_args.tuple()
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
                _minAmountLd=swap_proposal.min_to_amount.Wei,
                _lzTxParams=lz_tx_params.tuple(),
                _to=address,
                _payload='0x'
            )

            tx_params['data'] = router_contract.encodeABI(
                'swap', args=tx_args.tuple()
            )

        tx_params['value'] = int(fee.Wei * multiplier)

        return tx_params, swap_info, swap_proposal

    async def _estimate_send_tokens_fee(
        self,
        stg_contract: Contract,
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
        router_contract: Contract,
        dst_chain_id: int,
        lz_tx_params: TxArgs,
    ) -> TokenAmount:
        result = await router_contract.functions.quoteLayerZeroFee(
            dst_chain_id,
            1,
            self.client.account.address,
            '0x',
            lz_tx_params.list()
        ).call()

        return TokenAmount(amount=result[0], wei=True)

    async def _quote_send_fee(
        self,
        router_contract: Contract,
        swap_query: SwapQuery,
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
                swap_query.amount_from.Wei,
                swap_query.min_to_amount.Wei,
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
class Stargate(Base):
    async def bridge(
        self,
    ):
        settings = Settings()
        dst_bridge_data = Config.STARGATE_ROUTES_FOR_BRIDGE

        random_networks = list(dst_bridge_data.keys())
        random.shuffle(random_networks)

        logger.info(
            f'{self.client.account.address} | Stargate | Started to search enough balance for bridge')
        for network in random_networks:
            client = Client(
                private_key=self.client.account._private_key,
                network=network,
                proxy=self.client.proxy
            )

            dst_data = None
            random_tokens = list(dst_bridge_data[network].keys())
            random.shuffle(random_tokens)

            found_token_symbol, found_amount_from = None, 0

            for token_sym in random_tokens:
                token_contract = ContractsFactory.get_contract(
                    network.name, token_sym)
                if token_contract.is_native_token:
                    balance = await client.wallet.balance()

                    if float(balance.Ether) < settings.bridge_eth_amount.from_:
                        continue

                    amount_from = settings.bridge_eth_amount.from_
                    amount_to = min(float(balance.Ether), settings.bridge_eth_amount.to_)
                    min_percent = settings.bridge_eth_amount_percent.from_
                    max_percent = settings.bridge_eth_amount_percent.to_
                else:
                    balance = await client.wallet.balance(token_contract)

                    if float(balance.Ether) < settings.bridge_stables_amount.from_:
                        continue

                    amount_from = settings.bridge_stables_amount.from_
                    amount_to = min(float(balance.Ether), settings.bridge_stables_amount.to_)
                    min_percent = settings.bridge_stables_amount_percent.from_
                    max_percent = settings.bridge_stables_amount_percent.to_

                swap_info = SwapInfo(
                    src_network=network,
                    src_token_name=token_sym,
                    amount_from=amount_from,
                    amount_to=amount_to,
                    min_percent=min_percent,
                    max_percent=max_percent
                )
                client = client
                dst_data = dst_bridge_data[network][token_sym]
                found_token_symbol = swap_info.src_token_name
                found_amount_from = (
                    swap_info.amount
                    if swap_info.amount
                    else round(swap_info.amount_by_percent * float(balance.Ether), 6)
                )

            if dst_data:
                logger.info(
                    f'{self.client.account.address} | Found {found_amount_from} '
                    f'{found_token_symbol} in {network.name.capitalize()}!'
                )
                break

        if not dst_data:
            return 'Stargate | Failed to bridge: not found enough balance in native or tokens in any network'

        random_dst_data = random.choice(dst_data)
        swap_info.dst_network = random_dst_data[0]
        swap_info.dst_token_name = random_dst_data[1]
        stargate = StargateImplementation(client)

        return await stargate.bridge(swap_info, settings.max_bridge_fee_usd)
# endregion Random function
