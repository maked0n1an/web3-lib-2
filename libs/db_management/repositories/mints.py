from abc import ABC

from .generic import GenericRepository, GenericSqlAlchemyRepository
from ..models import Mint


class MintRepositoryBase(GenericRepository[Mint], ABC):
    pass


class MintRepository(GenericSqlAlchemyRepository[Mint], MintRepositoryBase):
    pass
