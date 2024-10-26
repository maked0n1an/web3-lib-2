from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import BridgeORM


class BridgeRepositoryBase(GenericRepository[BridgeORM], ABC):
    pass


class BridgeRepository(GenericSqlAlchemyRepository[BridgeORM], BridgeRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, BridgeORM)