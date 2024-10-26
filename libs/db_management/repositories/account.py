from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import AccountORM


class AccountRepositoryBase(GenericRepository[AccountORM], ABC):
    @abstractmethod
    async def get_by_evm_private_key(self, pk: str) -> AccountORM | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_evm_address(self, address: str) -> AccountORM | None:
        raise NotImplementedError()


class AccountRepository(GenericSqlAlchemyRepository[AccountORM], AccountRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AccountORM)
    
    async def get_by_evm_private_key(self, pk: str) -> AccountORM | None:
        return await self.get_with_filters(
            {'evm_private_key': pk}
        )

    async def get_by_evm_address(self, address: str) -> AccountORM | None:
        return await self.get_with_filters(
            {'evm_address': address}
        )
