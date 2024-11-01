from abc import (
    ABC, abstractmethod
)
from typing import (
    Generic, List, Type, TypeVar
)

from ..models import SqlBaseModel


TEntity = TypeVar("TEntity", bound=SqlBaseModel)


class GenericRepository(Generic[TEntity], ABC):
    @abstractmethod
    async def get(self, id: int) -> TEntity | None:
        raise NotImplementedError()
    
    @abstractmethod
    async def get_with_filters(self, filters: dict) -> TEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self, filters) -> List[TEntity] | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_with_filters(self, filters: dict) -> List[TEntity]:
        raise NotImplementedError()

    @abstractmethod
    async def add(self, entity: TEntity) -> int:
        raise NotImplementedError()

    @abstractmethod
    async def add_all(self, entities: List[TEntity]) -> List[int]:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, entity: TEntity) -> int:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> bool:
        raise NotImplementedError()