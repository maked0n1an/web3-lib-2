from sqlalchemy.ext.asyncio import AsyncSession

from .services.account import AccountService
from .services.bridges import BridgeService
from .services.mints import MintService
from .services.stakes import StakeService
from .services.swaps import GenericService
from ..data_access.repository.sql_alchemy import GenericSqlAlchemyRepository

from ..__init__ import async_engine


class ServiceUnitOfWork:
    async def __aenter__(self):
        self.__session = AsyncSession(bind=async_engine,expire_on_commit=False)
        
        self.accounts = AccountService(GenericSqlAlchemyRepository(self.__session))
        self.bridges = BridgeService(GenericSqlAlchemyRepository(self.__session))
        self.mints = MintService(GenericSqlAlchemyRepository(self.__session))
        self.stakes = StakeService(GenericSqlAlchemyRepository(self.__session))
        self.swaps = GenericService(GenericSqlAlchemyRepository(self.__session))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e
        finally:
            await self.__session.close()
        