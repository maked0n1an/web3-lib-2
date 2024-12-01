from typing import List

from ._generic import Service
from ...data_access.repositories.mints import MintRepository
from ...core.dtos import GetByAccountId, MintDTO
from ...core.helpers import ServiceResult


class MintService(Service[MintDTO]):
    def __init__(self, repository: MintRepository):
        self.repository = repository

    async def get_all_by_account_id(
        self,
        account_id: int
    ) -> ServiceResult[List[MintDTO]]:
        entities = await self.get_all(
            filters=GetByAccountId(account_id)
        )
        dtos = [self.dto_type.model_validate(entity) for entity in entities]

        return (
            ServiceResult.create_success(dtos)
            if len(dtos) > 0
            else ServiceResult.create_failure(f'No mints found with account ID {account_id}')
        )
    
    async def count_mints(
        self,
        account_id: int
    ) -> ServiceResult[int]:
        count = await self.repository.count(account_id)

        return (
            ServiceResult.create_success(count)
            if count > 0
            else ServiceResult.create_failure(f'No mints found with account ID {account_id}')
        )
