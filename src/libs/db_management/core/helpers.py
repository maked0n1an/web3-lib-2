from typing import Generic, TypeVar


TValue = TypeVar('TValue', bound=object)


class ServiceResult(Generic[TValue]):
    def __init__(self, is_success: bool, value: TValue | None, error: str):
        self.is_success = is_success
        self.value = value
        self.error = error

    @classmethod
    def create_success(cls, value: TValue) -> 'ServiceResult[TValue]':
        return cls(is_success=True, value=value, error='')

    @classmethod
    def create_failure(cls, error: str) -> 'ServiceResult[TValue]':
        return cls(is_success=False, value=None, error=error)
