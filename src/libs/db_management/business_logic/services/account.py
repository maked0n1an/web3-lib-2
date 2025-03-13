from typing import List
from sqlalchemy.exc import SQLAlchemyError

from ._generic import Service
from ...core.dtos import AccountDTO
from ...core.helpers import ServiceResult
from ...data_access.repositories.accounts import AccountRepository


class AccountService(Service[AccountDTO]):
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    async def get_by_evm_private_key(
        self,
        evm_private_key: str
    ) -> ServiceResult[AccountDTO]:
        if (
            not evm_private_key.startswith('0x')
            and len(evm_private_key) != 66
        ):
            return ServiceResult.create_failure('Invalid EVM private key')

        return await self.get_one(
            filters=AccountDTO.GetByEvmPrivateKey(evm_private_key)
        )

    async def get_by_evm_address(
        self,
        evm_address: str
    ) -> ServiceResult[AccountDTO]:
        if not evm_address.startswith('0x') and len(evm_address) != 40:
            return ServiceResult.create_failure('Invalid EVM address')

        return await self.get_one(
            filters=AccountDTO.GetByEvmAddress(evm_address)
        )

    async def add(self, dto: AccountDTO) -> ServiceResult[int | None]:
        try:
            return await super().add(dto)
        except SQLAlchemyError as e:
            error_message = str(e.__dict__['orig'])

            if 'UNIQUE constraint failed' in error_message:
                error_message = (
                    f"Entity with the same EVM address '{dto.evm_address}' and "
                    f"private key '{dto.evm_private_key}' already exists in database"
                )

            return ServiceResult.create_failure(error_message)

    async def add_all(self, dtos: List[AccountDTO]) -> ServiceResult[List[int] | None]:
        try:
            return await super().add_all(dtos)
        except SQLAlchemyError as e:
            error_message = str(e.__dict__['orig'])

            if 'UNIQUE constraint failed' in error_message:
                error_message = (
                    f'In this list of entities some entity with the same EVM address '
                    f'and private key already exists in database'
                )

            return ServiceResult.create_failure(error_message)
        
    async def update(self, dto: AccountDTO) -> ServiceResult[AccountDTO | None]:
        try:
            return await super().update(dto)
        except SQLAlchemyError as e:
            error_message = str(e.__dict__['orig'])

            if 'UNIQUE constraint failed' in error_message:
                error_message = (
                    f"Cannot update EVM address or private key"
                )

            return ServiceResult.create_failure(error_message)
