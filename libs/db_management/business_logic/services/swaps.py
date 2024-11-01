from typing import List

from .generic import GenericService
from ..dtos import SwapDTO
from ..helpers.service_result import ServiceResult
from ...data_access.models import SwapEntity
from ...data_access.repository.sql_alchemy import GenericRepository


class SwapService(GenericService[SwapDTO]):
    def __init__(self, repository: GenericRepository[SwapEntity]):
        super().__init__(repository)

    async def get_all_by_account_id(
        self, 
        account_id: int
    ) -> ServiceResult[List[SwapDTO]]:
        entities = await self.repository.get_all_with_filters({'account_id': account_id})
        
        self.object_mapper.create_map(self.repository.entity_type, self.dto_type)
        dtos = [self.object_mapper.map(entity, self.dto_type) for entity in entities]
        
        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
        )