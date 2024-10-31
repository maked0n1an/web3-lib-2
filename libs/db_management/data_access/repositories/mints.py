from abc import ABC, abstractmethod
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import MintEntity


class MintRepositoryBase(GenericRepository[MintEntity], ABC):
    @abstractmethod
    async def get_all_by_account_id(self, account_id: int) -> List[MintEntity]:
        raise NotImplementedError()


class MintRepository(GenericSqlAlchemyRepository[MintEntity], MintRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MintEntity)

    async def get_all_by_account_id(self, account_id: int) -> List[MintEntity]:
        return await self.get_all_with_filters({'account_id': account_id})