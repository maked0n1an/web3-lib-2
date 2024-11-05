from abc import ABC, abstractmethod
from typing import (
    Type, 
    Generic, 
    TypeVar, 
    List
)

from ..entities import SqlBaseModel


TEntity = TypeVar("TEntity", bound=SqlBaseModel)


class GenericRepository(Generic[TEntity], ABC):
    entity_type: Type[TEntity]

    @abstractmethod
    async def get_by_id(self, id: int) -> TEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_with_filters(self, filters: dict) -> TEntity | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self) -> List[TEntity] | None:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_with_filters(self, filters: dict) -> List[TEntity] | None:
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
