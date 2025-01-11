from sqlalchemy import select, func

from ...core.entities import BridgeEntity
from ...data_access.repositories._generic import GenericSqlRepository


class BridgeRepository(GenericSqlRepository[BridgeEntity]):
    async def count(
        self,
        account_id: int
    ) -> int:
        query = select(func.count()).where(
            self.entity_type.account_id == account_id
        )
        result = await self.__session.execute(query)
        return result.scalar_one()
    
    async def count_volume(
        self,
        account_id: int
    ) -> float | None:
        query = select(func.sum(self.entity_type.volume_usd)).where(
            self.entity_type.account_id == account_id
        )
        result = await self.__session.execute(query)
        return result.scalar_one_or_none()
