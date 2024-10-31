from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import BridgeEntity


class BridgeRepositoryBase(GenericRepository[BridgeEntity], ABC):
    @abstractmethod
    async def get_all_by_account_id(self, account_id: int) -> List[BridgeEntity]:
        raise NotImplementedError()


class BridgeRepository(GenericSqlAlchemyRepository[BridgeEntity], BridgeRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BridgeEntity)
        
