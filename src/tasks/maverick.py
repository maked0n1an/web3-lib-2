import random
import time
from eth_typing import HexStr

from web3 import Web3
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from user_data._inputs.settings._global import MODULES_SETTINGS_FILE_PATH
from src.helpers.time_functions import sleep
from src.libs.async_eth_lib.architecture.client import EvmClient
from src.libs.async_eth_lib.data.token_contracts import TokenContractData, ZkSyncEraTokenContracts
from src.libs.async_eth_lib.models.contract import RawContract
from src.libs.async_eth_lib.models.others import LogStatus, TokenAmount, TokenSymbol
from src.libs.async_eth_lib.models.operation import OperationInfo, TxPayloadDetails, TxPayloadDetailsFetcher
from src.libs.async_eth_lib.models.transaction import TxArgs
from src.libs.async_eth_lib.utils.helpers import read_json
from src.tasks._common.evm_task import EvmTask
from src.tasks._common.utils import (
    PriceUtils, RandomChoiceHelper, StandardSettings
)

# region Settings
class MaverickSettings():
    def __init__(self):
        settings = read_json(path=MODULES_SETTINGS_FILE_PATH)
        self.swap = StandardSettings(
            settings=settings,
            module_name='maverick',
            action_name='swap'
        )
# endregion Settings


# region Pools and paths
class MaverickData(TxPayloadDetailsFetcher):
    LIQUIDITY_POOLS = {
        (TokenSymbol.ETH, TokenSymbol.USDC):
            "0x41c8cf74c27554a8972d3bf3d2bd4a14d8b604ab",            
        (TokenSymbol.USDC, TokenSymbol.BUSD):
            "0xe799043fb52ff46cc57ce8a8b1ac3f151ba270f7",
        (TokenSymbol.USDC, TokenSymbol.ETH):
            "0x74a8f079eb015375b5dbb3ee98cbb1b91089323f",
        (TokenSymbol.BUSD, TokenSymbol.ETH):
            "0x3ae63fb198652e294b8de4c2ef659d95d5ff28be"
    }

    PATHS = {
        TokenSymbol.ETH: {
            TokenSymbol.USDC: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    LIQUIDITY_POOLS[(TokenSymbol.ETH, TokenSymbol.USDC)],
                    ZkSyncEraTokenContracts.USDC.address
                ]
            ),
            TokenSymbol.BUSD: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncEraTokenContracts.WETH.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.ETH)],
                    ZkSyncEraTokenContracts.USDC.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.BUSD)],
                    ZkSyncEraTokenContracts.BUSD.address,
                ]
            ),
        },
        TokenSymbol.BUSD: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncEraTokenContracts.BUSD.address,
                    LIQUIDITY_POOLS[(TokenSymbol.BUSD, TokenSymbol.ETH)],
                    ZkSyncEraTokenContracts.WETH.address,
                ]
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncEraTokenContracts.USDC.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.ETH)],
                    ZkSyncEraTokenContracts.WETH.address,
                ]
            )
        }
    }
# endregion Pools and paths


# region Implementation
class MaverickImplementation(EvmTask):
    def __init__(self, client: EvmClient):
        super().__init__(client)
        self.__raw_router_contract = RawContract(
            title="Maverick Router",
            address="0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4",
            abi_path=("data", "abis", "zksync", "maverick", "router_abi.json")
        )

    async def swap(self, swap_info: OperationInfo) -> bool:
        is_result = False
        swap_proposal = await self.create_operation_proposal(swap_info)

        from_token_price = await PriceUtils.get_cex_price(swap_info.from_token_name)
        to_token_price = await PriceUtils.get_cex_price(swap_info.to_token_name)

        min_to_amount = float(swap_proposal.amount_from.Ether) * from_token_price \
            / to_token_price
        
        swap_proposal.min_amount_to = TokenAmount(
            amount=min_to_amount,
            decimals=self.client.network.decimals,
            wei=True
        )

        tx_payload_details = MaverickData.get_tx_payload_details(
            first_token=swap_info.from_token_name,
            second_token=swap_info.to_token_name
        )
        encoded_path_payload = b''
        for address in tx_payload_details.swap_path:
            encoded_path_payload += Web3.to_bytes(hexstr=HexStr(address))

        account_address = self.client.account.address
        contract = self.client.contract.get_evm_contract_from_raw(
            self.__raw_router_contract
        )       
         
        if swap_info.from_token_name != TokenSymbol.ETH:
            recipient_address = TokenContractData.ZERO_ADDRESS
            second_data = contract.encodeABI('unwrapWETH9', args=[
                swap_proposal.min_amount_to.Wei,
                self.client.account.address,
            ])
            
        else:    
            recipient_address = account_address
            second_data = contract.encodeABI('refundETH', args=[])      

        params = TxArgs(
            path=encoded_path_payload,
            recipient=recipient_address,
            deadline=int(time.time() + 10 * 60),
            amountIn=swap_proposal.amount_from.Wei,
            amountOutMinimum=swap_proposal.min_amount_to.Wei
        )
        
        swap_amount_data = contract.encodeABI(
            tx_payload_details.method_name,
            args=[params.get_list()]
        )            

        multicall_data = contract.encodeABI(
            'multicall',
            args=[
                [swap_amount_data, second_data]
            ]
        )

        tx_params = TxParams(
            to=contract.address,
            data=multicall_data,
            maxPriorityFeePerGas=0,
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
            
            if is_result:
                status = LogStatus.SWAPPED
                message = ''

            else:
                status = LogStatus.FAILED
                message = f'Swap'

            message += (
                f'{rounded_amount_from} {swap_proposal.from_token.title}'
                f' -> {rounded_amount_to} {swap_proposal.to_token.title}: '
                f'{full_path + tx.hash.hex()}'
            )
        except web3_exceptions.ContractCustomError as e:
            self.client.custom_logger.log_message(
                status=LogStatus.ERROR,
                message='Failed to swap, trying to make slippage more...'
            )
            swap_info.slippage *= 1.3
            return await self.swap(swap_info)
        except Exception as e:
            message = str(e)
            status = LogStatus.ERROR

        self.client.custom_logger.log_message(status, message)
        return is_result
# endregion Implementation


# region Random function
class Maverick:
    def __init__(self, client: EvmClient):
        self.client = client

    async def bridge(self) -> bool:
        settings = MaverickSettings()
        swap_routes = get_maverick_swap_routes()
        
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
                    'Failed to bridge: not found enough balance in native or tokens in any network'
                )
            )
            return False

        operation_info.to_token_name = random.choice(dst_data)
        maverick = MaverickImplementation(client)

        return await maverick.swap(operation_info)
# endregion Random function
