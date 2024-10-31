from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import AccountEntity


class AccountRepositoryBase(GenericRepository[AccountEntity], ABC):
    @abstractmethod
    async def get_by_evm_private_key(
        self, 
        pk: str
    ) -> AccountEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_evm_address(
        self, 
        address: str
    ) -> AccountEntity | None:
        raise NotImplementedError()


class AccountRepository(GenericSqlAlchemyRepository[AccountEntity], AccountRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AccountEntity)
    
    async def get_by_evm_private_key(
        self, 
        pk: str
    ) -> AccountEntity | None:
        return await self.get_with_filters({'evm_private_key': pk})

    async def get_by_evm_address(
        self, 
        address: str
    ) -> AccountEntity | None:
        return await self.get_with_filters({'evm_address': address})
