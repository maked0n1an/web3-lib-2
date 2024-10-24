from sqlalchemy.ext.asyncio import AsyncSession

from .models import Account
from .abstractions import (
    AccountRepositoryBase, GenericSqlAlchemyRepository
)


class AccountRepository(GenericSqlAlchemyRepository[Account], AccountRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Account)

    async def get_by_evm_private_key(self, pk: str) -> Account | None:
        filters = {'evm_private_key': pk}

        return await self.get_with_filters(filters)

    async def get_by_evm_address(self, address: str) -> Account | None:
        filters = {'evm_address': address}

        return await self.get_with_filters(filters)
