from typing import TypeVar, Generic


TValue = TypeVar('TValue', bound=object)

class ServiceResult(Generic[TValue]):
    def __init__(self, success: bool, value: TValue, error: str):
        self.success = success
        self.value = value
        self.error = error
    
    @classmethod
    def create_success(cls, value: TValue) -> 'ServiceResult[TValue]':
        return cls(success=True, value=value, error='')
    
    @classmethod
    def create_failure(cls, error: str) -> 'ServiceResult[TValue]':
        return cls(success=False, value=None, error=error)
