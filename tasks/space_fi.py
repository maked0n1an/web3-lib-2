import random
import time

import web3.exceptions as web3_exceptions
from web3.types import TxParams

from data.config import MODULES_SETTINGS_FILE_PATH
from libs.async_eth_lib.architecture.client import Client
from libs.async_eth_lib.data.networks import Networks
from libs.async_eth_lib.data.token_contracts import ZkSyncEraTokenContracts
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.utils.decorators import validate_swap_tokens
from libs.async_eth_lib.utils.helpers import read_json, sleep
from libs.async_eth_lib.models.others import (
    LogStatus, TokenSymbol
)
from libs.async_eth_lib.models.operation import (
    OperationInfo, OperationProposal, TxPayloadDetails, TxPayloadDetailsFetcher
)
from tasks._common.utils import BaseTask, RandomChoiceHelper, StandardSettings
from tasks.config import get_space_fi_paths


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
class SpaceFiImplementation(BaseTask):
    SPACE_FI_ROUTER = RawContract(
        title='SpaceFiRouter',
        address='0xbE7D1FD1f6748bbDefC4fbaCafBb11C6Fc506d1d',
        abi_path=('data', 'abis', 'zksync', 'space_fi', 'abi.json')
    )

    @validate_swap_tokens(SpaceFiRoutes.PATHS.keys())
    async def swap(
        self,
        swap_info: OperationInfo
    ) -> bool:
        contract = await self.client.contract.get(
            contract=self.SPACE_FI_ROUTER
        )
        account_address = self.client.account.address

        swap_proposal = await self._create_swap_proposal(swap_info=swap_info)
        tx_payload_details = SpaceFiRoutes.get_tx_payload_details(
            first_token=swap_info.from_token_name,
            second_token=swap_info.to_token_name
        )

        if swap_info.from_token_name != TokenSymbol.ETH:
            memory_address = 128 + 32
        else:
            memory_address = 128

        data = [
            f'{tx_payload_details.function_signature}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(swap_proposal.min_amount_to.Wei))}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(memory_address))}',
            f'{self.to_cut_hex_prefix_and_zfill(account_address).lower()}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(int(time.time() + 20 * 60)))}',
            f'{self.to_cut_hex_prefix_and_zfill(hex(len(tx_payload_details.swap_path)))}'
        ]

        for contract_address in tx_payload_details.swap_path:
            data.append(
                self.to_cut_hex_prefix_and_zfill(contract_address.lower())
            )

        if swap_info.from_token_name != TokenSymbol.ETH:
            data.insert(1, self.to_cut_hex_prefix_and_zfill(
                hex(swap_proposal.amount_from.Wei)))

        data = ''.join(data)

        tx_params = TxParams(
            to=contract.address,
            data=data,
            maxPriorityFeePerGas=0
        )

        if not swap_proposal.from_token.is_native_token:
            is_approved = await self.approve_interface(
                operation_info=swap_info,
                token_contract=swap_proposal.from_token,
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

            tx = await self.client.transaction.sign_and_send(
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
                message = f'Failed swap'

            message += (
                f'{rounded_amount_from} {swap_info.from_token_name}'
                f' -> {rounded_amount_to} {swap_info.to_token_name}: '
                f'{full_path + tx.hash.hex()}'
            )

            self.client.custom_logger.log_message(
                status, message
            )

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
        swap_info: OperationInfo
    ) -> OperationProposal:
        swap_proposal = await self.compute_source_token_amount(
            operation_info=swap_info
        )

        swap_proposal.to_token = ZkSyncEraTokenContracts.get_token(
            swap_info.to_token_name
        )

        from_token_price = await self.get_binance_ticker_price(swap_info.from_token_name)
        second_token_price = await self.get_binance_ticker_price(swap_info.to_token_name)

        min_to_amount = float(swap_proposal.amount_from.Ether) * from_token_price \
            / second_token_price

        return await self.compute_min_destination_amount(
            operation_proposal=swap_proposal,
            min_to_amount=min_to_amount,
            operation_info=swap_info
        )
# endregion Implementation


# region Random function
class SpaceFi(BaseTask):
    async def swap(self) -> bool:
        settings = SpaceFiSettings()
        client = Client(
            account_id=self.client.account_id,
            private_key=self.client.account._private_key,
            network=Networks.zkSync_Era,
            proxy=self.client.proxy
        )
        client.custom_logger.log_message(
            status=LogStatus.INFO,
            message='Started to search enough balance for swap'
        )
        
        (operation_info, dst_data) = await RandomChoiceHelper.get_random_token_for_operation(
            op_name='swap',
            op_data=get_space_fi_paths(),
            op_settings=settings.swap,
            client=client
        )
             
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