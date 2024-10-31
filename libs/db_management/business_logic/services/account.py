from abc import ABC, abstractmethod
from mapper.object_mapper import ObjectMapper

from .generic import GenericService
from ..dtos import AccountDTO
from ..helpers.service_result import ServiceResult
from ...data_access.repositories.account import AccountRepositoryBase

class AccountServiceBase(GenericService[AccountDTO], ABC):
    @abstractmethod
    async def get_by_evm_private_key(
        self, 
        evm_private_key: str
    ) -> ServiceResult[AccountDTO]:
        pass
    
    @abstractmethod
    async def get_by_evm_address(
        self, 
        evm_address: str
    ) -> ServiceResult[AccountDTO]:
        pass


class AccountService(AccountServiceBase):
    def __init__(self, account_repository: AccountRepositoryBase):
        self.account_repository = account_repository
        self.object_mapper = ObjectMapper()
    
    async def get_by_evm_private_key(
        self, 
        evm_private_key: str
    ) -> ServiceResult[AccountDTO]:
        if not evm_private_key.startswith('0x'):
            if len(evm_private_key) != 64:
                raise ValueError('Invalid len of EVM private key')
        elif len(evm_private_key) > 66:
            raise ValueError('Invalid len of EVM private key')
        
        account = await self.account_repository.get_by_evm_private_key(evm_private_key)
        
        print(f"AccountEntity: {self.account_repository.model_cls}, type: {type(self.account_repository.model_cls)}")  # Отладочный вывод

        self.object_mapper.create_map(AccountEntity, AccountDTO)
        dto = self.object_mapper.map(account, AccountDTO)
        
        return (
            ServiceResult.create_success(dto) 
            if account is not None
            else ServiceResult.create_failure('Account with this EVM private key not found')
        )
        
    async def get_by_evm_address(
        self, 
        evm_address: str
    ) -> ServiceResult[AccountDTO]:
        if not evm_address.startswith('0x'):
            if len(evm_address) != 42:
                raise ValueError('Invalid len of EVM address')
        elif len(evm_address) > 42:
            raise ValueError('Invalid len of EVM address')
        
        account = await self.account_repository.get_by_evm_address(evm_address)
        self.object_mapper.create_map(AccountEntity, AccountDTO)
        dto = self.object_mapper.map(account, AccountDTO)
       
        return (
            ServiceResult.create_success(dto)
            if account is not None
            else ServiceResult.create_failure('Account with this EVM address not found')
        )
        
    

    