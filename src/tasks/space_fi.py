import random
import time

import web3.exceptions as web3_exceptions
from web3.types import TxParams

from user_data._inputs.settings._global import MODULES_SETTINGS_FILE_PATH
from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import ZkSyncEraTokenContracts
from src.libs.async_eth_lib.models.contract import RawContract
from src.libs.async_eth_lib.utils.helpers import read_json
from src.libs.async_eth_lib.models.others import LogStatus
from src.libs.async_eth_lib.models.operation import (
    OperationInfo, 
    TxPayloadDetails, 
    TxPayloadDetailsFetcher
)
from src._types.tokens import TokenSymbol
from src.tasks._common.evm_task import EvmTask
from src.tasks._common.utils import RandomChoiceHelper, StandardSettings, HexUtils
from src.tasks.config import get_space_fi_paths


# region Settings
class SpaceFiSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)
        self.swap = StandardSettings(
            settings=settings,
            module_name='space_fi',
            action_name='swap'
        )


# region Available paths
class SpaceFiRoutes(TxPayloadDetailsFetcher):
    PATHS = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.USDC.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.USDT: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.USDT.address
                ],
                function_signature="0x7ff36ab5"
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactETHForToken',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.WBTC.address
                ],
                function_signature="0x7ff36ab5"
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.SPACE.address,
                    ZkSyncEraTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.WBTC: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.WETH.address,
                    ZkSyncEraTokenContracts.WBTC.address
                ],
                function_signature='0x38ed1739'
            )
        },
        TokenSymbol.USDT: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.USDT.address,
                    # ZkSyncTokenContracts.SPACE.address,
                    ZkSyncEraTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            )
        },
        TokenSymbol.WBTC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.WBTC.address,
                    ZkSyncEraTokenContracts.USDC.address,
                    ZkSyncEraTokenContracts.WETH.address
                ],
                function_signature="0x18cbafe5"
            ),
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='swapExactTokensForETH',
                addresses=[
                    ZkSyncEraTokenContracts.WBTC.address,
                    ZkSyncEraTokenContracts.USDC.address
                ],
                function_signature='0x38ed1739'
            )
        }
    }
# endregion Available routes


# region Implementation
class SpaceFiImplementation(EvmTask):
    def __init__(self, client: EvmClient):
        super().__init__(client)
        self.__raw_router_contract = RawContract(
            title='SpaceFiRouter',
            address='0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d',
            abi_path=('data', 'abis', 'zksync', 'space_fi', 'abi.json')
        )

    async def swap(
        self,
        swap_info: OperationInfo
    ) -> bool:
        is_result = False
        account_address = self.client.account.address
        contract = self.client.contract.get_evm_contract_from_raw(
            self.__raw_router_contract
        )

        swap_proposal = await self.create_operation_proposal(swap_info)
        tx_payload_details = SpaceFiRoutes.get_tx_payload_details(
            first_token=swap_info.from_token_name,
            second_token=swap_info.to_token_name
        )

        if swap_info.from_token_name != TokenSymbol.ETH:
            memory_address = 128 + 32
        else:
            memory_address = 128

        data = [
            hex(swap_proposal.min_amount_to.Wei),
            hex(memory_address),
            str(account_address).lower(),
            hex(int(time.time() + 20 * 60)),
            hex(len(tx_payload_details.swap_path)),
        ]

        if swap_info.from_token_name != TokenSymbol.ETH:
            data.insert(0, hex(swap_proposal.amount_from.Wei))

        data_hex = [
            HexUtils.to_cut_hex_prefix_and_zfill(item) 
            for item in data
        ]
        data_hex += [
            HexUtils.to_cut_hex_prefix_and_zfill(contract_address.lower())
            for contract_address in tx_payload_details.swap_path
        ]

        data = tx_payload_details.function_signature + ''.join(data_hex)

        tx_params = TxParams(
            to=contract.address,
            data=data,
            maxPriorityFeePerGas=0
        )

        if not swap_proposal.from_token.is_native_token:
            is_approved = await self.approve_interface(
                operation_info=swap_info,
                token_address=swap_proposal.from_token,
                tx_params=tx_params,
                amount=swap_proposal.amount_from,
            )

            if is_approved:
                self.client.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{swap_proposal.amount_from.Ether} {swap_proposal.from_token.title}"
                )
                await sleep(8, 16)
        else:
            tx_params['value'] = swap_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                operation_info=swap_info,
                tx_params=tx_params
            )

            tx = await self.client.transaction.sign_and_send(tx_params)
            receipt = await tx.wait_for_tx_receipt(self.client.w3)

            full_path = (
                self.client.network.explorer
                + self.client.network.TX_PATH
            )
            rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(swap_proposal.min_amount_to.Ether, 5)
            is_result = receipt['status']

            if receipt['status']:
                log_status = LogStatus.SWAPPED
                message = ''

            else:
                log_status = LogStatus.FAILED
                message = f'Failed swap'

            message += (
                f'{rounded_amount_from} {swap_info.from_token_name}'
                f' -> {rounded_amount_to} {swap_info.to_token_name}: '
                f'{full_path + tx.hash.hex()}'
            )
        except web3_exceptions.ContractCustomError as e:
            message = 'Try to make slippage more'
            log_status = LogStatus.ERROR
        except Exception as e:
            if 'insufficient funds for gas + value' in str(e):
                message = 'Insufficient funds for gas + value'

            else:
                message = str(e)

            log_status = LogStatus.ERROR

        self.client.custom_logger.log_message(log_status, message)

        return is_result
# endregion Implementation


# region Random function
class SpaceFi(EvmTask):
    async def swap(self) -> bool:
        settings = SpaceFiSettings()
        swap_routes = get_space_fi_paths()

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
        space_fi = SpaceFiImplementation(client=client)

        return await space_fi.swap(operation_info)
# endregion Random function
