import random
import time

import web3.exceptions as web3_exceptions
from web3.types import TxParams

from data.config import MODULES_SETTINGS_FILE_PATH
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.data.token_contracts import ContractsFactory, ZkSyncTokenContracts
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from libs.async_eth_lib.models.others import (
    LogStatus, ParamsTypes, TokenSymbol
)
from libs.async_eth_lib.models.swap import (
    OperationInfo, SwapProposal, TxPayloadDetails, TxPayloadDetailsFetcher
)
from libs.pretty_utils.type_functions.dataclasses import FromTo
from tasks._common.utils import BaseTask
from tasks.config import Config

# region Settings
class MuteSettings():
    def __init__(self):
        mute_settings = read_json(path=MODULES_SETTINGS_FILE_PATH)

        self.swap_eth_amount: FromTo = FromTo(
            from_=mute_settings['swap_eth_amount']['from'],
            to_=mute_settings['swap_eth_amount']['to']
        )
        self.swap_eth_amount_percent: FromTo = FromTo(
            from_=mute_settings['swap_eth_amount']['min_percent'],
            to_=mute_settings['swap_eth_amount']['max_percent']
        )
        self.swap_stables_amount: FromTo = FromTo(
            from_=mute_settings['swap_stables_amount']['from'],
            to_=mute_settings['swap_stables_amount']['to']
        )
        self.swap_stables_amount_percent: FromTo = FromTo(
            from_=mute_settings['swap_stables_amount']['min_percent'],
            to_=mute_settings['swap_stables_amount']['max_percent']
        )
        self.slippage: int = mute_settings['slippage']
# endregion Settings


# region Implementation
class MuteImplementation(BaseTask):
    MUTE_UNIVERSAL = RawContract(
        title='Mute',
        address='0x8b791913eb07c32779a16750e3868aa8495f5964',
        abi=read_json(
            path=('data', 'abis', 'zksync', 'mute', 'abi.json')
        )
    )

    async def swap(
        self,
        swap_info: OperationInfo
    ) -> bool:
        check_message = self.validate_swap_inputs(
            first_arg=swap_info.from_token_name,
            second_arg=swap_info.to_token_name,
            param_type='tokens'
        )
        if check_message:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False

        contract = await self.client.contract.get(
            contract=self.MUTE_UNIVERSAL
        )

        swap_proposal = await self._create_swap_proposal(
            contract=contract,
            swap_info=swap_info
        )

        tx_payload_details = MuteRoutes.get_tx_payload_details(
            first_token=swap_info.from_token_name,
            second_token=swap_info.to_token_name
        )

        params = TxArgs(
            amountOutMin=swap_proposal.min_amount_to.Wei,
            path=tx_payload_details.swap_path,
            to=self.client.account.address,
            deadline=int(time.time() + 20 * 60),
            stable=tx_payload_details.bool_list
        )

        list_params = params.get_list()

        if (
            swap_info.from_token_name != TokenSymbol.ETH
        ):
            list_params.insert(0, swap_proposal.amount_from.Wei)

        tx_params = TxParams(
            to=contract.address,
            data=contract.encodeABI(
                tx_payload_details.method_name,
                args=tuple(list_params)
            ),
            maxPriorityFeePerGas=0
        )

        if not swap_proposal.from_token.is_native_token:
            hexed_tx_hash = await self.approve_interface(
                swap_info=swap_info,
                token_contract=swap_proposal.from_token,
                tx_params=tx_params,
                amount=swap_proposal.amount_from
            )

            if hexed_tx_hash:
                self.client.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{swap_proposal.amount_from.Ether} {swap_proposal.from_token.title}"
                )
                await sleep(8, 15)
        else:
            tx_params['value'] = swap_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                operation_info=swap_info,
                tx_params=tx_params
            )

            tx = await self.client.contract.sign_and_send(
                tx_params=tx_params
            )
            receipt = await tx.wait_for_tx_receipt(
                web3=self.client.w3
            )

            full_path = (
                self.client.network.explorer
                + self.client.network.TX_PATH
            )
            rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(swap_proposal.min_amount_to.Ether, 5)

            if receipt['status']:
                status = LogStatus.SWAPPED
                message = ''

            else:
                status = LogStatus.FAILED
                message = f'Swap'

            message += (
                f'{rounded_amount_from} {swap_info.from_token_name}'
                f' -> {rounded_amount_to} {swap_info.to_token_name}: '
                f'{full_path + tx.hash.hex()}'
            )

            self.client.custom_logger.log_message(
                status, message)

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

    async def _create_swap_proposal(
        self,
        contract: ParamsTypes.Contract,
        swap_info: OperationInfo
    ) -> SwapProposal:
        swap_proposal = await self.compute_source_token_amount(swap_info=swap_info)

        if swap_info.from_token_name == TokenSymbol.ETH:
            from_token = ZkSyncTokenContracts.WETH
        else:
            from_token = swap_proposal.from_token
        
        if swap_info.to_token_name == TokenSymbol.ETH:
            swap_proposal.to_token = ZkSyncTokenContracts.WETH
        else:
            swap_proposal.to_token = ZkSyncTokenContracts.get_token(
                swap_info.to_token_name
            )

        min_amount_out = await contract.functions.getAmountOut(
            swap_proposal.amount_from.Wei,
            from_token.address,
            swap_proposal.to_token.address
        ).call()

        return await self.compute_min_destination_amount(
            swap_proposal=swap_proposal,
            min_to_amount=min_amount_out[0],
            swap_info=swap_info,
            is_to_token_price_wei=True
        )
# endregion Implementation


# region Available paths
class MuteRoutes(TxPayloadDetailsFetcher):
    PATHS = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactETHForTokensSupportingFeeOnTransferTokens',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.USDT.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                bool_list=[False, False]
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.USDT.address,
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address,
                ],
                bool_list=[False, False, False]
            ),
        },
        TokenSymbol.USDT: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    # TokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address,
                ],
                bool_list=[True,
                           #    False,
                           False
                           ]
            ),
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.USDT.address,
                    ZkSyncTokenContracts.USDC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.WBTC.address
                ],
                bool_list=[False, True, True, False]
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.WETH.address,
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDT.address
                ],
                bool_list=[False, False, False]
            ),
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncTokenContracts.WBTC.address,
                    ZkSyncTokenContracts.WETH.address,
                    ZkSyncTokenContracts.USDC.address
                ],
                bool_list=[False, False, False]
            )
        }
    }
# endregion Available routes


# region Random function
class Mute(BaseTask):
    async def swap(
        self,
    ) -> bool:
        settings = MuteSettings()
        dst_swap_data = Config.MUTE_PATHS
        
        client = Client(
            account_id=self.client.account_id,
            private_key=self.client.account._private_key,
            network=Networks.ZkSync,
            proxy=self.client.proxy
        )
        client.custom_logger.log_message(
            status=LogStatus.INFO,
            message='Started to search enough balance for swap'
        )
        
        dst_data = None
        token_paths = list(dst_swap_data[Networks.ZkSync].keys())
        random.shuffle(token_paths)
        
        for token_symbol in token_paths:
            token_contract = ContractsFactory.get_contract(
                Networks.ZkSync.name, token_symbol
            )
            if token_contract.is_native_token:
                balance = await client.contract.get_balance()

                if (
                    float(balance.Ether) <= settings.swap_eth_amount.from_
                    and settings.swap_eth_amount.from_ == 0
                ):
                    continue

                amount_from = settings.swap_eth_amount.from_
                amount_to = min(float(balance.Ether), settings.swap_eth_amount.to_)
                min_percent = settings.swap_eth_amount_percent.from_
                max_percent = settings.swap_eth_amount_percent.to_
            else:
                balance = await client.contract.get_balance(token_contract)

                if (
                    float(balance.Ether) <= settings.swap_stables_amount.from_
                    and settings.swap_stables_amount.from_ == 0
                ):
                    continue

                amount_from = settings.swap_stables_amount.from_
                amount_to = min(float(balance.Ether), settings.swap_stables_amount.to_)
                min_percent = settings.swap_stables_amount_percent.from_
                max_percent = settings.swap_stables_amount_percent.to_

            swap_info = OperationInfo(
                from_token_name=token_symbol,
                amount_from=amount_from,
                amount_to=amount_to,
                slippage=settings.slippage,
                min_percent=min_percent,
                max_percent=max_percent
            )
            
            dst_data = dst_swap_data[Networks.ZkSync][token_symbol]
            found_token_symbol = swap_info.from_token_name
            found_amount_from = (
                swap_info.amount
                if swap_info.amount
                else round(swap_info.amount_by_percent * float(balance.Ether), 6)
            )
            
            if dst_data:
                self.client.custom_logger.log_message(
                    status=LogStatus.INFO,
                    message=(
                        f'Found {found_amount_from} '
                        f'{found_token_symbol} for swap!'
                    )
                )
                break
             
        if not dst_data:
            self.client.custom_logger.log_message(
                status=LogStatus.WARNING,
                message=(
                    'Failed to swap: not found enough balance in native or tokens'
                )
            )
            return False
            
        swap_info.to_token_name = random.choice(dst_data)
        mute = MuteImplementation(client=client)
        
        return await mute.swap(swap_info)
# endregion Random function