from abc import ABC

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import Swap


class SwapRepositoryBase(GenericRepository[Swap], ABC):
    pass


class SwapRepository(GenericSqlAlchemyRepository[Swap], SwapRepositoryBase):
    pass
