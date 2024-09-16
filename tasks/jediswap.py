import time

from starknet_py.net.client_models import TransactionExecutionStatus

from libs.async_starknet_lib.models.others import (
    LogStatus, 
    TokenSymbol
)
from libs.async_starknet_lib.models.operation import OperationInfo
from libs.async_starknet_lib.utils.decorators import validate_swap_tokens
from tasks._common.starknet_task import StarknetTask
    

AVAILABLE_COINS_FOR_SWAP = [
    TokenSymbol.USDC, 
    TokenSymbol.DAI,
    TokenSymbol.USDT,
    TokenSymbol.WBTC,
    TokenSymbol.ETH
]


class JediSwap(StarknetTask):
    @validate_swap_tokens(AVAILABLE_COINS_FOR_SWAP,'JediSwap')
    async def swap(self, swap_info: OperationInfo):
        swap_router = 0x041fd22b238fa21cfcf5dd45a8548974d8263b3a531a60388411c5e230f97023
        router_abi = ('data', 'abis', 'jediswap', 'router_abi.json')
        
        swap_proposal = await self.create_operation_proposal(swap_info)
        from_token_contract = self.client.contract.get_token_contract(
            token=swap_proposal.from_token
        )
        router_contract = self.client.contract.get_starknet_contract(
            address=swap_router, abi_or_path=router_abi
        )
        
        approve_call = from_token_contract.functions['approve'].prepare_call(
            spender=swap_router,
            amount=swap_proposal.amount_from.Wei
        )
        
        if swap_proposal.from_token.is_native_token:
            function_name = 'swap_tokens_for_exact_tokens'
            swap_args = {
                'amountOut': swap_proposal.amount_from.Wei,
                'amountInMax': swap_proposal.min_amount_to.Wei,
                
            }
        else:
            function_name = 'swap_exact_tokens_for_tokens'
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
                result = True
            else:
                log_status = LogStatus.ERROR
                message = 'Failed swap'
                result = False
                
            message += (
                f' {rounded_amount_from} {swap_proposal.from_token.title}'
                f' -> {rounded_amount_to} {swap_proposal.to_token.title}: '
                f'https://starkscan.co/tx/{hex(tx_receipt.transaction_hash)}'
            )
        except Exception as e:
            log_status = LogStatus.FAILED
            message = str(e)
            result = False
        
        self.client.custom_logger.log_message(
            status=log_status,
            message=message,
            call_place=__class__.__name__
        )
            
        return result
# endregion Implementation