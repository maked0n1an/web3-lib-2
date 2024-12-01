from typing import List

from ._generic import Service
from ...core.dtos import GetByAccountId, StakeDTO
from ...core.helpers import ServiceResult
from ...data_access.repositories.stakes import StakeRepository


class StakeService(Service[StakeDTO]):
    def __init__(self, repository: StakeRepository):
        self.repository = repository

    async def get_all_by_account_id(
        self,
        account_id: int
    ) -> ServiceResult[List[StakeDTO]]:
        entities = await self.get_all(
            filters=GetByAccountId(account_id)
        )
        dtos = [self.dto_type.model_validate(entity) for entity in entities]

        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No stakes found with account ID {account_id}')
        )

    async def count_stakes(
        self,
        account_id: int
    ) -> ServiceResult[int]:
        count = await self.repository.count(account_id)

        return (
            ServiceResult.create_success(count)
            if count > 0
            else ServiceResult.create_failure(f'No stakes found with account ID {account_id}')
        )
