from ._generic import Service
from ..dtos import AccountDTO
from ..helpers.service_result import ServiceResult
from ...data_access.entities import AccountEntity
from ...data_access.repository._generic import GenericRepository


class AccountService(Service[AccountDTO]):
    def __init__(self, repository: GenericRepository[AccountEntity]):
        super().__init__(repository, AccountDTO)

    async def get_by_evm_private_key(
        self, 
        evm_private_key: str
    ) -> ServiceResult[AccountDTO]:
        if not evm_private_key.startswith('0x'):
            if len(evm_private_key) != 64:
                raise ValueError('Invalid len of EVM private key')
        elif len(evm_private_key) > 66:
            raise ValueError('Invalid len of EVM private key')
        
        account = await self.repository.get_with_filters({'evm_private_key': evm_private_key})
        dto = AccountDTO.model_validate(account)
        
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
        
        account = await self.repository.get_with_filters({'evm_address': evm_address})
        dto = AccountDTO.model_validate(account)
       
        return (
            ServiceResult.create_success(dto)
            if account is not None
            else ServiceResult.create_failure('Account with this EVM address not found')
        )
        
    

    