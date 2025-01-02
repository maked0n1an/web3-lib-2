import time

from starknet_py.net.client_models import TransactionExecutionStatus

from libs.async_starknet_lib.architecture.client import StarknetClient
from libs.async_starknet_lib.models.contract import RawContract
from libs.async_starknet_lib.utils.decorators import validate_operation_tokens
from libs.async_starknet_lib.models.operation import OperationInfo
from libs.async_starknet_lib.models.others import (
    LogStatus,
    TokenSymbol
)
from tasks._common.starknet_task import StarknetTask


class Swap10kSettings:
    AVAILABLE_FOR_SWAP = [
        TokenSymbol.USDC,
        TokenSymbol.DAI,
        TokenSymbol.USDT,
        TokenSymbol.WBTC,
        TokenSymbol.ETH
    ]


# region Implementation
class Swap10k(StarknetTask):
    def __init__(self, client: StarknetClient):
        super().__init__(client)
        self.__router_contract = RawContract(
            title='10kSwap Router',
            address=0x07a6f98c03379b9513ca84cca1373ff452a7462a3b61598f0af5bb27ad7f76d1,
            abi_path=('data', 'abis', '10kswap', 'router_abi.json')
        )
    
    @validate_operation_tokens(
        available_tokens=Swap10kSettings.AVAILABLE_FOR_SWAP,
        operation_name='swap',
        class_name='10kSwap'
    )
    async def swap(self, swap_info: OperationInfo) -> bool:
        is_result = False
        swap_proposal = await self.create_operation_proposal(swap_info)
        from_token_contract = self.client.contract.get_starknet_contract_from_raw(
            contract=swap_proposal.from_token
        )
        router_contract = self.client.contract.get_starknet_contract_from_raw(
            contract=self.__router_contract
        )
        
        if swap_proposal.from_token.is_native_token:
            function_name = 'swapTokensForExactTokens'
            swap_args = {
                'amountOut': swap_proposal.amount_from.Wei,
                'amountInMax': swap_proposal.min_amount_to.Wei,
            }
        else:
            function_name = 'swapExactTokensForTokens'
            swap_args = {
                'amountIn': swap_proposal.amount_from.Wei,
                'amountOutMin': swap_proposal.min_amount_to.Wei,
            }

        swap_args.update(
            {
                'path': [
                    swap_proposal.from_token.address,
                    swap_proposal.to_token.address,
                ],
                'to': self.client.account.address,
                'deadline': int(time.time() + 20*60)
            }
        )

        approve_call = from_token_contract.functions['approve'].prepare_call(
            spender=router_contract.address,
            amount=swap_proposal.amount_from.Wei
        )
        swap_call = router_contract.functions[function_name].prepare_call(
            **swap_args
        )
        try:
            response = await self.client.account.execute_v1(
                calls=[approve_call, swap_call],
                auto_estimate=True
            )

            tx_receipt = await self.client.node_client.wait_for_tx(
                response.transaction_hash
            )

            rounded_amount_from = round(swap_proposal.amount_from.Ether, 5)
            rounded_amount_to = round(swap_proposal.min_amount_to.Ether, 5)

            if tx_receipt.execution_status == TransactionExecutionStatus.SUCCEEDED:
                log_status = LogStatus.SWAPPED
                message = ''
                is_result = True
                
            else:
                log_status = LogStatus.FAILED
                message = 'Failed swap '

            message += (
                f'{rounded_amount_from} {swap_proposal.from_token.title}'
                f' -> {rounded_amount_to} {swap_proposal.to_token.title}: '
                f'https://starkscan.co/tx/{hex(tx_receipt.transaction_hash)}'
            )
        except Exception as e:
            message = str(e)
            log_status = LogStatus.ERROR
 
        self.client.custom_logger.log_message(log_status, message)

        return is_result
# endregion Implementation
