from sqlalchemy.ext.asyncio import AsyncSession

from .services.account import AccountService
from .services.bridges import BridgeService
from .services.mints import MintService
from .services.stakes import StakeService
from .services.swaps import SwapService
from ..data_access.repository.sql_alchemy import SqlAlchemyRepository
from ..data_access.entities import (
    AccountEntity, BridgeEntity, MintEntity, StakeEntity, SwapEntity
)

from .. import async_engine


class ServiceUnitOfWork:
    async def __aenter__(self):
        self.__session = AsyncSession(
            bind=async_engine, expire_on_commit=False)

        self.accounts = AccountService(
            SqlAlchemyRepository(self.__session, AccountEntity))
        self.bridges = BridgeService(
            SqlAlchemyRepository(self.__session, BridgeEntity))
        self.mints = MintService(
            SqlAlchemyRepository(self.__session, MintEntity))
        self.stakes = StakeService(
            SqlAlchemyRepository(self.__session, StakeEntity))
        self.swaps = SwapService(
            SqlAlchemyRepository(self.__session, SwapEntity))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e
        finally:
            await self.__session.close()
