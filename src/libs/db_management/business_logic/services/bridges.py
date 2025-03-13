from typing import List

from ._generic import Service
from ...data_access.repositories.bridges import BridgeRepository
from ...core.dtos import BridgeDTO, GetByAccountId
from ...core.helpers import ServiceResult


class BridgeService(Service[BridgeDTO]):
    def __init__(self, repository: BridgeRepository):
        self.repository = repository

    async def get_all_by_account_id(
        self,
        account_id: int
    ) -> ServiceResult[List[BridgeDTO]]:
        entities = await self.get_all(
            filters=GetByAccountId(account_id)
        )
        dtos = [self.dto_type.model_validate(entity) for entity in entities]

        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
        )

    async def count_bridges(
        self,
        account_id: int
    ) -> ServiceResult[int]:
        count = await self.repository.count(account_id)

        return (
            ServiceResult.create_success(count)
            if count > 0
            else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
        )
    
    async def count_volume(
        self,
        account_id: int
    ) -> ServiceResult[float | None]:
        volume = await self.repository.count_volume(account_id)

        return (
            ServiceResult.create_success(volume)
            if volume is not None
            else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
        )

