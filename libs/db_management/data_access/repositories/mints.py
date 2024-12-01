from sqlalchemy import select, func

from ...data_access.repositories._generic import GenericSqlRepository
from ...core.entities import MintEntity


class MintRepository(GenericSqlRepository[MintEntity]):
    async def count(
        self,
        account_id: int
    ) -> int:
        query = select(func.count()).where(
            self.entity_type.account_id == account_id
        )
        result = await self.__session.execute(query)
        return result.scalar_one()

