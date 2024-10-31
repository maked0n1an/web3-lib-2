from sqlalchemy.ext.asyncio import AsyncSession

from libs.db_management.business_logic.services.bridges import BridgeService
from libs.db_management.business_logic.services.generic import GenericService

from .services.account import AccountService
from ..data_access.repositories.account import AccountRepository
from ..data_access.repositories.bridges import BridgeRepository
from ..data_access.repositories.swaps import SwapRepository
from ..__init__ import async_engine


class ServiceUnitOfWork:
    async def __aenter__(self):
        self.__session = AsyncSession(bind=async_engine,expire_on_commit=False)
        self.accounts = AccountService(AccountRepository(self.__session))
        self.bridges = BridgeService(BridgeRepository(self.__session))
        # self.mints = MintService(self.__session)
        # self.stakes = StakeService(self.__session)
        self.swaps = GenericService(SwapRepository(self.__session))
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e
        finally:
            await self.__session.close()
        