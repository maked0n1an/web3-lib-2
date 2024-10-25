from abc import ABC, abstractmethod

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import Account


class AccountRepositoryBase(GenericRepository[Account], ABC):
    @abstractmethod
    async def get_by_evm_private_key(self, pk: str) -> Account | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_evm_address(self, address: str) -> Account | None:
        raise NotImplementedError()


class AccountRepository(GenericSqlAlchemyRepository[Account], AccountRepositoryBase):
    async def get_by_evm_private_key(self, pk: str) -> Account | None:
        return await self.get_with_filters(
            {'evm_private_key': pk}
        )

    async def get_by_evm_address(self, address: str) -> Account | None:
        return await self.get_with_filters(
            {'evm_address': address}
        )
