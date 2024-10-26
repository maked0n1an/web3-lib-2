from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import StakeORM


class StakeRepositoryBase(GenericRepository[StakeORM], ABC):
    pass


class StakeRepository(GenericSqlAlchemyRepository[StakeORM], StakeRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, StakeORM)
