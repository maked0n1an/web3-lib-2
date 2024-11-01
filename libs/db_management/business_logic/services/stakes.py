from typing import List

from .generic import GenericService
from ..helpers.service_result import ServiceResult
from ...data_access.models import StakeEntity
from ...data_access.repository.sql_alchemy import GenericRepository


class StakeService(GenericService[object]):
    def __init__(self, repository: GenericRepository[StakeEntity]):
        super().__init__(repository)
    
    async def get_all_by_account_id(
        self, 
        account_id: int
    ) -> ServiceResult[List[object]]:
        entities = await self.repository.get_all_with_filters({'account_id': account_id})
        
        self.object_mapper.create_map(self.repository.entity_type, self.dto_type)
        dtos = [self.object_mapper.map(entity, self.dto_type) for entity in entities]
        
        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
        )