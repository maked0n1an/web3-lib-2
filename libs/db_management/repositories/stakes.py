from abc import ABC

from ..models import Stake
from ..repositories.generic import GenericSqlAlchemyRepository


class StakeRepositoryBase(ABC):
    pass


class StakeRepository(GenericSqlAlchemyRepository[Stake], StakeRepositoryBase):
    pass
