from ..architecture.logger import console_logger
from ..models.operation import OperationInfo


def validate_operation_tokens(
    available_tokens: list[str],
    op_name: str,
    class_name: str
):
    def decorator(func):
        async def _wrapper(self, operation_info: OperationInfo, *args, **kwargs):
            from_token = operation_info.from_token_name
            to_token = operation_info.to_token_name

            if (
                from_token not in available_tokens
                or
                to_token not in available_tokens
            ):
                console_logger.error(
                    f'Not supported tokens to {op_name} in {class_name}:'
                    f' {from_token} or {to_token}'
                )
                return
            if from_token == to_token:
                console_logger.error(
                    f'The tokens for {op_name}() are equal in {class_name}:'
                    f' {from_token} == {to_token} '
                )
                return
            return await func(self, operation_info, *args, **kwargs)
        return _wrapper
    return decorator
