from abc import (
    ABC,
    abstractmethod
)
from typing import (
    Type,
    Generic,
    List,
    TypeVar
)

from ...core.dtos import GeneralDTO
from ...core.helpers import ServiceResult
from ...data_access.repositories._generic import (
    GenericRepository,
    TEntity
)


DTO = TypeVar("DTO", bound=GeneralDTO)


class GenericService(Generic[DTO], ABC):
    """
    Base service class for all models

    Use 'dto_type' to access the generic DTO type passed in the subclass
    """
    dto_type: Type[DTO]

    def __init_subclass__(cls):
        cls.dto_type = cls.__orig_bases__[0].__args__[0] #type: ignore

    @abstractmethod
    async def add(self, dto: DTO) -> ServiceResult[int]:
        raise NotImplementedError()

    @abstractmethod
    async def add_all(self, dtos: List[DTO]) -> ServiceResult[List[int] | None]:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_id(self, id: int) -> ServiceResult[DTO | None]:
        raise NotImplementedError()

    @abstractmethod
    async def get_one(self, filters: DTO) -> ServiceResult[DTO | None]:
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self) -> ServiceResult[List[DTO] | None]:
        raise NotImplementedError()

    @abstractmethod
    async def update(self, dto: DTO) -> ServiceResult[DTO | None]:
        raise NotImplementedError()
    
    @abstractmethod
    async def update_all(self, filters: DTO, values_dict: DTO) -> ServiceResult[int | None]:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> ServiceResult[bool]:
        raise NotImplementedError()
    
    @abstractmethod
    async def delete_all(self, filters: DTO) -> ServiceResult[List[bool] | None]:
        raise NotImplementedError()


class Service(GenericService[DTO], ABC):
    def __init__(
        self,
        repository: GenericRepository[TEntity]
    ):
        self.repository = repository
    
    async def get_by_id(self, id: int) -> ServiceResult[DTO | None]:
        entity = await self.repository.get_one_or_none_by_id(id)
        dto = self.dto_type.model_validate(entity)

        return (
            ServiceResult.create_success(dto)
            if entity is not None
            else ServiceResult.create_failure('Entity not found')
        )

    async def get_one(self, filters: DTO) -> ServiceResult[DTO | None]:
        filters_dict = filters.model_dump(exclude_unset=True)
        entity = await self.repository.get_one_or_none(filters_dict)
        dto = self.dto_type.model_validate(entity)

        return (
            ServiceResult.create_success(dto)
            if entity is not None
            else ServiceResult.create_failure('Entity not found')
        )

    async def get_all(self, filters: DTO | None = None) -> ServiceResult[List[DTO] | None]:
        filters_dict = (
            filters.model_dump(exclude_unset=True)
            if filters
            else {}
        )
        entities = await self.repository.get_all(filters_dict)
        dtos = [
            self.dto_type.model_validate(entity)
            for entity in entities
        ]

        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure('No entities found')
        )
    
    async def add(self, dto: DTO) -> ServiceResult[int | None]:
        values_dict = dto.model_dump(exclude_unset=True)
        entity = self.repository.entity_type(**values_dict)
        db_entity = await self.repository.add(entity)

        return (
            ServiceResult.create_success(db_entity.id)
            if db_entity.id > 0
            else ServiceResult.create_failure('Failed to add entity to database')
        )

    async def add_all(self, dtos: List[DTO]) -> ServiceResult[List[int] | None]:
        entities = [
            self.repository.entity_type(
                **dto.model_dump(exclude_unset=True)
            )
            for dto in dtos
        ]
        db_entities = await self.repository.add_all(entities)
        db_ids = [entity.id for entity in db_entities]

        return (
            ServiceResult.create_success(db_ids)
            if len(db_ids) > 0
            else ServiceResult.create_failure('Failed to add entities to database')
        )

    async def update(self, dto: DTO) -> ServiceResult[DTO | None]:
        values_dict = dto.model_dump(exclude_unset=True)
        db_entity = await self.repository.update_one_by_id(dto.id, values_dict)
        dto = self.dto_type.model_validate(db_entity)

        return (
            ServiceResult.create_success(dto)
            if db_entity is not None
            else ServiceResult.create_failure('Entity does not exist')
        )
    
    async def update_all(self, filters: DTO, values: list[DTO]) -> ServiceResult[int]:
        filters_dict = filters.model_dump(exclude_unset=True)
        values_dicts = [
            value.model_dump(exclude_unset=True)
            for value in values
        ]
        row_count = await self.repository.update_all(filters_dict, values_dicts)

        return (
            ServiceResult.create_success(row_count)
            if row_count > 0
            else ServiceResult.create_failure('Entities do not exist')
        )

    async def delete(self, id: int) -> ServiceResult[bool]:
        result = await self.repository.delete_one_by_id(id)

        return (
            ServiceResult.create_success(result)
            if result
            else ServiceResult.create_failure('Entity does not exist')
        )
    
    async def delete_all(self, filters: DTO) -> ServiceResult[int]:
        filters_dict = filters.model_dump(exclude_unset=True)
        result = await self.repository.delete_all(filters_dict)

        return (
            ServiceResult.create_success(result)
            if result
            else ServiceResult.create_failure('Entities do not exist')
        )
