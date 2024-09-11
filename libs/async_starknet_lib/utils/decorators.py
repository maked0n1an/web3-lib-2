from ..architecture.logger import console_logger
from ..models.operation import OperationInfo


def validate_swap_tokens(
    available_tokens: list[str],
    class_name: str
):
    def decorator(func):
        async def _wrapper(self, swap_info: OperationInfo):
            from_token = swap_info.from_token_name.upper()
            to_token = swap_info.to_token_name.upper()
            
            if (
                from_token not in available_tokens
                or
                to_token not in available_tokens
            ):
                console_logger.error(
                    f'Not supported tokens to swap in {class_name}:'
                    f' {from_token} or {to_token}'
                )
                return
            if from_token == to_token:
                console_logger.error(
                    f'The tokens for swap() are equal in {class_name}:'
                    f' {from_token} == {to_token} '
                )
                return
            return await func(self, swap_info)
        return _wrapper
    return decorator


def validate_liquidity_tokens(
    available_pools: list[str],
    class_name: str
):
    def decorator(func):
        async def _wrapper(self, liq_info: OperationInfo):
            from_token = liq_info.from_token_name
            to_token = liq_info.to_token_name
            pool_name = from_token + to_token
            
            if pool_name not in available_pools:
                console_logger.error(
                    f'Not supported pool \'{pool_name}\' '
                    f'to deposit/withdraw in {class_name}'
                )
                return
            return await func(self, liq_info)
        return _wrapper
    return decorator