from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import StakeEntity


class StakeRepositoryBase(GenericRepository[StakeEntity], ABC):
    @abstractmethod
    async def get_all_by_account_id(self, account_id: int) -> List[StakeEntity]:
        raise NotImplementedError()


class StakeRepository(GenericSqlAlchemyRepository[StakeEntity], StakeRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StakeEntity)
    
    async def get_all_by_account_id(self, account_id: int) -> List[StakeEntity]:
        return await self.get_all_with_filters({'account_id': account_id})
