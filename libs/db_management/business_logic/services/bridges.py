from typing import List

from ._generic import Service
from ..dtos import BridgeDTO
from ..helpers.service_result import ServiceResult
from ...data_access.entities import BridgeEntity
from ...data_access.repository._generic import GenericRepository


class BridgeService(Service[BridgeDTO]):
    def __init__(self, repository: GenericRepository[BridgeEntity]):
        super().__init__(repository, BridgeDTO)

    async def get_all_by_account_id(
        self, 
        account_id: int
    ) -> ServiceResult[List[BridgeDTO]]:
        entities = await self.repository.get_all_with_filters({'account_id': account_id})
        dtos = [BridgeDTO.model_validate(entity) for entity in entities]
        
        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
        )
