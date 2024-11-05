from typing import List

from ._generic import Service
# from ..dtos import MintDTO
from ..helpers.service_result import ServiceResult
from ...data_access.entities import MintEntity
from ...data_access.repository._generic import GenericRepository


class MintService(Service[object]):
    def __init__(self, repository: GenericRepository[MintEntity]):
        super().__init__(repository, object)
        
    # async def get_all_by_account_id(
    #     self, 
    #     account_id: int
    # ) -> ServiceResult[List[object]]:
    #     entities = await self.repository.get_all_with_filters({'account_id': account_id})
    #     dtos = [MintDTO.model_validate(entity) for entity in entities]
        
    #     return (
    #         ServiceResult.create_success(dtos)
    #         if len(dtos) > 0
    #         else ServiceResult.create_failure(f'No bridges found with account ID {account_id}')
    #     )