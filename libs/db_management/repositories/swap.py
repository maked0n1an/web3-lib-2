from abc import ABC

from .generic import GenericSqlAlchemyRepository
from ..models import Swap


class SwapRepositoryBase(ABC):
    pass


class SwapRepository(GenericSqlAlchemyRepository[Swap], SwapRepositoryBase):
    pass
