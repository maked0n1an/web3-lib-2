from abc import ABC

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import MintORM


class MintRepositoryBase(GenericRepository[MintORM], ABC):
    pass


class MintRepository(GenericSqlAlchemyRepository[MintORM], MintRepositoryBase):
    pass
