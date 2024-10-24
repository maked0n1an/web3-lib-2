from abc import (
    ABC, abstractmethod
)
from typing import (
    Generic, List, Tuple, Type, TypeVar
)

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from .models import SqlBaseModel, Account


Model = TypeVar("Model", bound=SqlBaseModel)


class GenericRepository(Generic[Model], ABC):
    @abstractmethod
    async def get(self, id: int) -> Model | None:
        raise NotImplementedError()
    
    @abstractmethod
    async def get_all(self, filters) -> List[Model]:
        raise NotImplementedError()
    
    @abstractmethod
    async def add(self, record: Model) -> Model:
        raise NotImplementedError()
    
    @abstractmethod
    async def update(self, record: Model) -> Model:
        """This method uses entity.id to search model"""
        raise NotImplementedError()
    
    @abstractmethod
    async def delete(self, record: Model) -> Model:
        raise NotImplementedError()
    

class GenericSqlAlchemyRepository(GenericRepository[Model], ABC):
    def __init__(self, session: AsyncSession, model_cls: Type[Model]):
        self.__session = session
        self.__model_cls = model_cls
    
    def _construct_search_query(self, **filters): 
        query = select(self.__model_cls)
        where_clauses = []
        for attr, value in filters.items():
            if not hasattr(self.__model_cls, attr):
                raise ValueError(f'Invalid column name {attr}')
            where_clauses.append(getattr(self.__model_cls, attr) == value)
        
        if len(where_clauses) == 1:
            query = query.where(where_clauses[0])
        elif len(where_clauses) > 1:
            query = query.where(and_(*where_clauses))
        
        return query
    
    async def get(self, id: int) -> Model | None:
        return await self.__session.get(self.__model_cls, id)
        
    async def get_with_filters(self, filters: dict) -> Model | None:
        query = self._construct_search_query(**filters).limit(1)
        return (await self.__session.execute(query)).scalar_one_or_none()
    
    async def get_all(self) -> List[Model]:
        return await self.get_all_with_filters({})
                
    async def get_all_with_filters(self, filters) -> List[Model]:
        query = self._construct_search_query(**filters)
        return (await self.__session.execute(query)).scalars().all()
    
    async def add(self, entity: Model) -> Model:
        self.__session.add(entity)
        await self.__session.flush()
    
    async def update(self, entity: Model) -> Model:
        await self.__session.merge(entity)
        await self.__session.commit()
    
    async def delete(self, entity: Model) -> None:
        query = (
            select(self.__model_cls)
            .where(self.__model_cls.id == entity.id)
        )
        db_record = await self.__session.scalar(query)
        if not db_record:
            return
        
        # db_record = await self.get(entity.id)
        await self.__session.delete(db_record)
        await self.__session.commit()
    

class AccountRepositoryBase(GenericRepository[Account], ABC):
    @abstractmethod
    async def get_by_evm_private_key(self, pk: str) -> Account | None:
        raise NotImplementedError()
    
    @abstractmethod
    async def get_by_evm_address(self, address: str) -> Account | None:
        raise NotImplementedError()