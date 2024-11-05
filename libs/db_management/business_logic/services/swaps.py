from typing import List

from ._generic import Service
from ..dtos import SwapDTO
from ..helpers.service_result import ServiceResult
from ...data_access.entities import SwapEntity
from ...data_access.repository._generic import GenericRepository


class SwapService(Service[SwapDTO]):
    def __init__(self, repository: GenericRepository[SwapEntity]):
        super().__init__(repository, SwapDTO)

    async def get_all_by_account_id(
        self, 
        account_id: int
    ) -> ServiceResult[List[SwapDTO]]:
        entities = await self.repository.get_all_with_filters({'account_id': account_id})
        dtos = [SwapDTO.model_validate(entity) for entity in entities]
        
        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No swaps found with account ID {account_id}')
        )