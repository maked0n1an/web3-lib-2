from abc import ABC

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import Stake


class StakeRepositoryBase(GenericRepository[Stake], ABC):
    pass


class StakeRepository(GenericSqlAlchemyRepository[Stake], StakeRepositoryBase):
    pass
