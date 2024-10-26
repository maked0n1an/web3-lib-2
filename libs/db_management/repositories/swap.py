from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import SwapORM


class SwapRepositoryBase(GenericRepository[SwapORM], ABC):
    pass


class SwapRepository(GenericSqlAlchemyRepository[SwapORM], SwapRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SwapORM)
