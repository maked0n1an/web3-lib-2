from typing import List

from .generic import GenericService
from ..dtos import BridgeDTO
from ..helpers.service_result import ServiceResult
from ...data_access.models import BridgeEntity
from ...data_access.repositories.bridges import BridgeRepositoryBase


class BridgeService(GenericService[BridgeDTO]):
    def __init__(self, bridge_repository: BridgeRepositoryBase):
        super().__init__(bridge_repository)
    
    async def get_all_by_account_id(
        self, 
        account_id: int
    ) -> ServiceResult[List[BridgeDTO]]:
        entities = await self.repository.get_all_with_filters({'account_id': account_id})
        self.object_mapper.create_map(BridgeEntity, BridgeDTO)
        dtos = [self.object_mapper.map(entity, BridgeDTO) for entity in entities]
        
        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
        )
