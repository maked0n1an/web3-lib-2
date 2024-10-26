from abc import ABC

from sqlalchemy.ext.asyncio import AsyncSession

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import MintORM


class MintRepositoryBase(GenericRepository[MintORM], ABC):
    pass


class MintRepository(GenericSqlAlchemyRepository[MintORM], MintRepositoryBase):
    def __init__(self, session: AsyncSession):
        super().__init__(session, MintORM)
