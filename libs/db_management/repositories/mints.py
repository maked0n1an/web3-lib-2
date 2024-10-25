from abc import ABC

from .generic import GenericSqlAlchemyRepository
from ..models import Mint


class MintRepositoryBase(ABC):
    pass


class MintRepository(GenericSqlAlchemyRepository[Mint], MintRepositoryBase):
    pass
