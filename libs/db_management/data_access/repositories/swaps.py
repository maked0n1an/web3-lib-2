from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import SwapEntity


class SwapRepositoryBase(GenericRepository[SwapEntity], ABC):
    @abstractmethod
    async def get_all_by_account_id(self, account_id: int) -> List[SwapEntity]:
        raise NotImplementedError()


class SwapRepository(GenericSqlAlchemyRepository[SwapEntity], SwapRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SwapEntity)

    async def get_all_by_account_id(self, account_id: int) -> List[SwapEntity]:
        return await self.get_all_with_filters({'account_id': account_id})
