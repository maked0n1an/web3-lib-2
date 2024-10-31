from abc import ABC, abstractmethod
from typing import List, TypeVar, Generic
from mapper.object_mapper import ObjectMapper

from libs.db_management.business_logic.dtos import GeneralDTO

from ..helpers.service_result import ServiceResult
from ...data_access.repositories.generic import GenericRepository, TEntity


DTO = TypeVar("DTO", bound=GeneralDTO)


class GenericServiceBase(Generic[DTO], ABC):
    @abstractmethod
    async def get(self, id: int) -> ServiceResult[DTO]:
        raise NotImplementedError()
    
    @abstractmethod
    async def get_with_filters(self, filters: dict) -> ServiceResult[DTO]:
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self, filters: dict) -> ServiceResult[List[DTO]]:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_with_filters(self, filters: dict) -> ServiceResult[List[DTO]]:
        raise NotImplementedError()

    @abstractmethod
    async def add(self, dto: DTO) -> ServiceResult[int]:
        raise NotImplementedError()

    @abstractmethod
    async def add_all(self, dtos: List[DTO]) -> ServiceResult[List[int]]:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, dto: DTO) -> ServiceResult[int]:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> ServiceResult[bool]:
        raise NotImplementedError()


class GenericService(GenericServiceBase):
    def __init__(self, repository: GenericRepository[DTO]):
        self.repository = repository
        self.object_mapper = ObjectMapper()
    
    async def add(self, dto: DTO) -> ServiceResult[int]:
        self.object_mapper.create_map(DTO, TEntity)
        entity = self.object_mapper.map(dto, TEntity)
        id = await self.repository.add(entity)
        return (
            ServiceResult.create_success(id)
            if id > 0
            else ServiceResult.create_failure('Failed to add entity to database')
        )
    
    async def add_all(self, dtos: List[DTO]) -> ServiceResult[List[int]]:
        self.object_mapper.create_map(DTO, TEntity)
        entities = [self.object_mapper.map(dto, TEntity) for dto in dtos]
        ids = await self.repository.add_all(entities)
        return ServiceResult.create_success(ids)
