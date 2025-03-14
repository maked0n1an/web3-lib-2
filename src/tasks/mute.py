import random
import time

import web3.exceptions as web3_exceptions
from web3.types import TxParams

from _types.explorer import ExplorerEndpoints
from src.helpers.time_functions import sleep
from user_data._inputs.settings._global import MODULES_SETTINGS_FILE_PATH
from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import ZkSyncEraTokenContracts
from src.libs.async_eth_lib.models.contract import RawContract
from src.libs.async_eth_lib.models.params_types import Web3ContractType
from src.libs.async_eth_lib.models.transaction import TxArgs
from src.libs.async_eth_lib.utils.helpers import read_json
from src.libs.async_eth_lib.models.others import (
    LogStatus, TokenSymbol
)
from src.libs.async_eth_lib.models.operation import (
    OperationInfo, OperationProposal, TxPayloadDetails, TxPayloadDetailsFetcher
)
from src.tasks._common.evm_task import EvmTask
from src.tasks._common.utils import RandomChoiceHelper, StandardSettings
from src.tasks.config import get_mute_paths


# region Settings
class MuteSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)
        self.swap = StandardSettings(
            settings=settings,
            module_name='mute',
            action_name='swap'
        )
# endregion Settings


# region Available paths
class MuteRoutes(TxPayloadDetailsFetcher):
    PATHS = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactETHForTokensSupportingFeeOnTransferTokens',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.USDC.address
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.USDT.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactETHForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.WBTC.address
                ],
                bool_list=[False, False]
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.WETH.address
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.USDT.address,
                ],
                bool_list=[True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.WBTC.address,
                ],
                bool_list=[False, False, False]
            ),
        },
        TokenSymbol.USDT: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.USDT.address,
                    # TokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.USDC.address,
                ],
                bool_list=[True,
                           #    False,
                           False
                           ]
            ),
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.USDT.address,
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.WETH.address,
                ],
                bool_list=[True, True, False]
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.USDT.address,
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.WBTC.address
                ],
                bool_list=[False, True, True, False]
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.WBTC.address,
                    ZkSyncEraTokenContracts.WETH.address,
                ],
                bool_list=[False, False]
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.WBTC.address,
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.USDT.address
                ],
                bool_list=[False, False, False]
            ),
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForTokens',
                addresses=[
                    ZkSyncEraTokenContracts.WBTC.address,
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.USDC.address
                ],
                bool_list=[False, False, False]
            )
        }
    }
# endregion Available routes


# region Implementation
class MuteImplementation(EvmTask):
    def __init__(self, client: EvmClient):
        super.__init__(client)
        self.__raw_router_contract = RawContract(
            title='Mute',
            address='0x8b791913eb07c32779a16750e3868aa8495f5964',
            abi_path=('data', 'abis', 'zksync', 'mute', 'abi.json')
        )

    async def swap(
        self,
        swap_info: OperationInfo
    ) -> bool:
        is_result = False
        contract = self.client.contract.get_evm_contract_from_raw(
            self.__raw_router_contract
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
            is_approved = await self.approve_interface(
                operation_info=swap_info,
                token_address=swap_proposal.from_token,
                tx_params=tx_params,
                amount=swap_proposal.amount_from
            )

            if is_approved:
                self.client.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{swap_proposal.amount_from.Ether} {swap_proposal.from_token.title}"
                )
                await sleep([8, 15])
        else:
            tx_params['value'] = swap_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                operation_info=swap_info,
                tx_params=tx_params
            )

            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt()

            full_path = (
                self.client.network.explorer
                + ExplorerEndpoints.TX
            )
            rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(swap_proposal.min_amount_to.Ether, 5)
            is_result = receipt['status']

            if is_result:
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
        except web3_exceptions.ContractCustomError as e:
            message = 'Try to make slippage more'
            status = LogStatus.ERROR
        except Exception as e:
            message = str(e)
            status = LogStatus.ERROR

        self.client.custom_logger.log_message(status, message)

        return is_result

    async def _create_swap_proposal(
        self,
        contract: Web3ContractType,
        swap_info: OperationInfo
    ) -> OperationProposal:
        swap_proposal = await self.init_operation_proposal(swap_info)

        if swap_info.from_token_name == TokenSymbol.ETH:
            swap_proposal.from_token = ZkSyncEraTokenContracts.WETH

        if swap_info.to_token_name == TokenSymbol.ETH:
            swap_proposal.to_token = ZkSyncEraTokenContracts.WETH

        min_amount_out = await contract.functions.getAmountOut(
            swap_proposal.amount_from.Wei,
            swap_proposal.from_token.address,
            swap_proposal.to_token.address
        ).call()

        return await self.complete_operation_proposal(
            operation_proposal=swap_proposal,
            slippage=swap_info.slippage,
            min_amount_to_wei=min_amount_out[0],
        )
# endregion Implementation


# region Random function
class Mute:
    def __init__(self, client: EvmClient):
        self.client = client

    async def swap(self) -> bool:
        settings = MuteSettings()
        swap_routes = get_mute_paths()

        random_networks = list(swap_routes)
        random.shuffle(random_networks)

        self.client.custom_logger.log_message(
            status=LogStatus.INFO,
            message='Started to search enough balance for swap'
        )

        for network in random_networks:
            client = EvmClient(
                account_id=self.client.account_id,
                private_key=self.client.account._private_key,
                network=network,
                proxy=self.client.proxy
            )

            (operation_info, dst_data) = await RandomChoiceHelper.get_partial_operation_info_and_dst_data(
                op_data=swap_routes,
                op_settings=settings.swap,
                client=client
            )

            if operation_info:
                break

        if not dst_data:
            self.client.custom_logger.log_message(
                status=LogStatus.WARNING,
                message=(
                    'Failed to swap: not found enough balance in native or tokens'
                )
            )
            return False

        operation_info.to_token_name = random.choice(dst_data)
        mute = MuteImplementation(client=client)

        return await mute.swap(operation_info)
# endregion Random function
