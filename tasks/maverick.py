import time
from eth_typing import HexStr

from web3 import Web3
from web3.types import TxParams
import web3.exceptions as web3_exceptions

from libs.async_eth_lib.data.token_contracts import TokenContractData, ZkSyncTokenContracts
from libs.async_eth_lib.models.contract import RawContract
from libs.async_eth_lib.models.others import LogStatus, TokenSymbol
from libs.async_eth_lib.models.swap import SwapInfo, TxPayloadDetails, TxPayloadDetailsFetcher
from libs.async_eth_lib.models.transaction import TxArgs
from libs.async_eth_lib.utils.helpers import read_json, sleep
from tasks._common.utils import BaseTask


# region Implementation
class Maverick(BaseTask):
    MAVERICK_ROUTER = RawContract(
        title="Maverick Router",
        address="0x39E098A153Ad69834a9Dac32f0FCa92066aD03f4",
        abi=read_json(
            path=("data", "abis", "zksync", "maverick", "router_abi.json")
        ),
    )

    async def swap(
        self,
        swap_info: SwapInfo
    ) -> bool:
        check_message = self.validate_swap_inputs(
            first_arg=swap_info.from_token_name,
            second_arg=swap_info.to_token_name,
            param_type='tokens'
        )
        if check_message:
            self.client.account_manager.custom_logger.log_message(
                status=LogStatus.ERROR, message=check_message
            )

            return False
        
        is_src_token_eth = swap_info.from_token_name == TokenSymbol.ETH
        
        swap_proposal = await self.compute_source_token_amount(
            swap_info=swap_info
        )
        swap_proposal.to_token = ZkSyncTokenContracts.get_token(
            swap_info.to_token_name
        )

        from_token_price = await self.get_binance_ticker_price(swap_info.from_token_name)
        second_token_price = await self.get_binance_ticker_price(swap_info.to_token_name)

        min_to_amount = float(swap_proposal.amount_from.Ether) * from_token_price \
            / second_token_price

        swap_proposal = await self.compute_min_destination_amount(
            swap_proposal=swap_proposal,
            min_to_amount=min_to_amount,
            swap_info=swap_info
        )

        tx_payload_details = MaverickData.get_tx_payload_details(
            first_token=swap_info.from_token_name,
            second_token=swap_info.to_token_name
        )
        encoded_path_payload = b''
        for address in tx_payload_details.swap_path:
            encoded_path_payload += Web3.to_bytes(hexstr=HexStr(address))

        account_address = self.client.account_manager.account.address
        contract = await self.client.contract.get(
            contract=self.MAVERICK_ROUTER
        )       
         
        if not is_src_token_eth:
            recipient_address = TokenContractData.ZERO_ADDRESS
            second_data = contract.encodeABI('unwrapWETH9', args=[
                swap_proposal.min_amount_to.Wei,
                self.client.account_manager.account.address,
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
            hexed_tx_hash = await self.approve_interface(
                swap_info=swap_info,
                token_contract=swap_proposal.from_token,
                tx_params=tx_params,
                amount=swap_proposal.amount_from,
            )

            if hexed_tx_hash:
                self.client.account_manager.custom_logger.log_message(
                    LogStatus.APPROVED,
                    message=f"{swap_proposal.amount_from.Ether} {swap_proposal.from_token.title}"
                )
                await sleep(8, 16)
        else:
            tx_params['value'] = swap_proposal.amount_from.Wei

        try:
            tx_params = self.set_all_gas_params(
                swap_info=swap_info,
                tx_params=tx_params
            )

            tx = await self.client.contract.transaction.sign_and_send(
                tx_params=tx_params
            )
            receipt = await tx.wait_for_tx_receipt(
                web3=self.client.account_manager.w3
            )

            full_path = (
                self.client.account_manager.network.explorer
                + self.client.account_manager.network.TX_PATH
            )
            rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(swap_proposal.min_amount_to.Ether, 5)

            if receipt['status']:
                status = LogStatus.SWAPPED
                message = ''

            else:
                status = LogStatus.ERROR
                message = f'Failed swap'

            message += (
                f'{rounded_amount_from} {swap_info.from_token_name}'
                f' -> {rounded_amount_to} {swap_info.to_token_name}: '
                f'{full_path + tx.hash.hex()}'
            )

            self.client.account_manager.custom_logger.log_message(
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

        self.client.account_manager.custom_logger.log_message(status, message)

        return False
# endregion Implementation


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
                    ZkSyncTokenContracts.WETH.address,
                    LIQUIDITY_POOLS[(TokenSymbol.ETH, TokenSymbol.USDC)],
                    ZkSyncTokenContracts.USDC.address
                ]
            ),
            TokenSymbol.BUSD: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.WETH.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.ETH)],
                    ZkSyncTokenContracts.USDC.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.BUSD)],
                    ZkSyncTokenContracts.BUSD.address,
                ]
            ),
        },
        TokenSymbol.BUSD: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.BUSD.address,
                    LIQUIDITY_POOLS[(TokenSymbol.BUSD, TokenSymbol.ETH)],
                    ZkSyncTokenContracts.WETH.address,
                ]
            )
        },
        TokenSymbol.USDC: {
            TokenSymbol.ETH: TxPayloadDetails(
                method_name='exactInput',
                addresses=[
                    ZkSyncTokenContracts.USDC.address,
                    LIQUIDITY_POOLS[(TokenSymbol.USDC, TokenSymbol.ETH)],
                    ZkSyncTokenContracts.WETH.address,
                ]
            )
        }
    }
# endregion Pools and paths