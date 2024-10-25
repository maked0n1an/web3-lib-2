from abc import ABC

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import SwapORM


class SwapRepositoryBase(GenericRepository[SwapORM], ABC):
    pass


class SwapRepository(GenericSqlAlchemyRepository[SwapORM], SwapRepositoryBase):
    pass
