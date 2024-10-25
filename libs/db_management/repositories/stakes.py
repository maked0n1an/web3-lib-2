from abc import ABC

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import StakeORM


class StakeRepositoryBase(GenericRepository[StakeORM], ABC):
    pass


class StakeRepository(GenericSqlAlchemyRepository[StakeORM], StakeRepositoryBase):
    pass
