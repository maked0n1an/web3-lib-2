from abc import ABC, abstractmethod
from typing import (
    Type, 
    Generic, 
    TypeVar, 
    List
)

from mapper.object_mapper import ObjectMapper


from ..dtos import AccountDTO, GeneralDTO
from ..helpers.service_result import ServiceResult
from ...data_access.repository.sql_alchemy import GenericRepository, TEntity
from ...data_access.entities import AccountEntity


DTO = TypeVar("DTO", bound=GeneralDTO)


class GenericService(Generic[DTO], ABC):
    dto_type: Type[DTO]

    @abstractmethod
    async def get_by_id(self, id: int) -> ServiceResult[DTO | None]:
        raise NotImplementedError()
    
    @abstractmethod
    async def get_with_filters(self, filters: DTO) -> ServiceResult[DTO | None]:
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self) -> ServiceResult[List[DTO] | None]:
        raise NotImplementedError()

    @abstractmethod
    async def get_all_with_filters(self, filters: DTO) -> ServiceResult[List[DTO] | None]:
        raise NotImplementedError()

    @abstractmethod
    async def add(self, dto: DTO) -> ServiceResult[int | None]:
        raise NotImplementedError()

    @abstractmethod
    async def add_all(self, dtos: List[DTO]) -> ServiceResult[List[int] | None]:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, dto: DTO) -> ServiceResult[int | None]:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> ServiceResult[bool]:
        raise NotImplementedError()


class Service(GenericService[DTO], ABC):
    def __init__(
        self, 
        repository: GenericRepository[TEntity],
        dto_type: Type[DTO]
    ):
        self.repository = repository
        self.dto_type = dto_type

    async def get_by_id(self, id: int) -> ServiceResult[DTO | None]:
        entity = await self.repository.get_by_id(id)

        mapper = ObjectMapper()
        mapper.create_map(
            type(type((entity))), 
            self.dto_type
        )
        dto = mapper.map(entity, self.dto_type)

        return (
            ServiceResult.create_success(dto)
            if entity is not None
            else ServiceResult.create_failure('Entity not found')
        )
    
    async def get_with_filters(self, filters: DTO) -> ServiceResult[DTO | None]:
        filter_dict = filters.model_dump(exclude_unset=True)
        entity = await self.repository.get_with_filters(**filter_dict)
        dto = self.dto_type.model_validate(entity)
        
        return (
            ServiceResult.create_success(dto)
            if entity is not None
            else ServiceResult.create_failure('Entity not found')
        )
    
    async def get_all(self, filters: DTO) -> ServiceResult[List[DTO] | None]:
        filter_dict = filters.model_dump(exclude_unset=True)
        entities = await self.repository.get_all(filter_dict)
        dtos = [
            self.dto_type.model_validate(entity)
            for entity in entities
        ]

        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure('No entities found')
        )
    
    async def get_all_with_filters(self, filters: DTO) -> ServiceResult[List[DTO] | None]:
        filter_dict = filters.model_dump(exclude_unset=True)
        entities = await self.repository.get_all_with_filters(filter_dict)

        return (
            ServiceResult.create_success(entities)
            if len(entities) > 0
            else ServiceResult.create_failure('No entities found')
        )
    
    async def add(self, dto: DTO) -> ServiceResult[int | None]:
        entity = dto.validate_back(self.repository.entity_type)
        id = await self.repository.add(entity)
        
        return (
            ServiceResult.create_success(id)
            if id > 0
            else ServiceResult.create_failure('Failed to add entity to database')
        )
    
    async def add_all(self, dtos: List[DTO]) -> ServiceResult[List[int] | None]:
        entities = [
            dto.validate_back(self.repository.entity_type) 
            for dto in dtos
        ]
        ids = await self.repository.add_all(entities)
        
        return (
            ServiceResult.create_success(ids)
            if ids > 0
            else ServiceResult.create_failure('Failed to add entity to database')
        )
    
    async def update(self, dto: DTO) -> ServiceResult[int | None]:
        entity = dto.validate_back(self.repository.entity_type)        
        id = await self.repository.update(entity)
        
        return (
            ServiceResult.create_success(id)
            if id > 0
            else ServiceResult.create_failure('Failed to update entity in database')
        )
    
    async def delete(self, id: int) -> ServiceResult[bool]:
        result = await self.repository.delete(id)
        
        return (
            ServiceResult.create_success(result)
            if result
            else ServiceResult.create_failure('Failed to delete entity from database')
        )