import inspect
import os

from ..architecture.logger import console_logger
from ..models.operation import OperationInfo

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