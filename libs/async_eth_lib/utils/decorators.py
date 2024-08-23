import inspect
import os

import libs.async_eth_lib.models.exceptions as exceptions
from libs.async_eth_lib.architecture.api_clients.evm import Account
from libs.async_eth_lib.architecture.logger import console_logger
from libs.async_eth_lib.models.operation import OperationInfo

def validate_swap_tokens(
    available_tokens: list[str],
    call_depth: str = 2
):
    def decorator(func):
        caller_frame = inspect.currentframe()
        for _ in range(call_depth):
            caller_frame = caller_frame.f_back
        calling_line = f"{os.path.basename(caller_frame.f_code.co_filename)}:{caller_frame.f_lineno}"
        
        async def _wrapper(self, swap_info: OperationInfo, *args, **kwargs):
            from_token = swap_info.from_token_name.upper()
            to_token = swap_info.to_token_name.upper()
            
            if (
                from_token not in available_tokens
                or
                to_token not in available_tokens
            ):
                message = (
                    f'Not supported tokens to swap:'
                    f' {from_token} or {to_token}'
                )
                console_logger.error(f"{calling_line:<15} | {message}")
                return
            
            if from_token == to_token:
                message = (
                    f'The tokens for swap() are equal:'
                    f' {from_token} == {to_token} '
                )
                console_logger.error(f"{calling_line:<15} | {message}")
                return
            
            return await func(self, swap_info, *args, **kwargs)
        
        return _wrapper
    return decorator


def api_key_required(func):
    """Check if the Blockscan API key is specified"""
     
    def func_wrapper(self:Account, *args, **kwargs):
        if not self.api_key:
            raise exceptions.ApiException('To use this function, you must specify the explorer API key!')

        else:
            return func(self, *args, **kwargs)
        
    return func_wrapper