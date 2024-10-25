from sqlalchemy.ext.asyncio import AsyncSession


from .db_init import async_engine
from .repositories.account import AccountRepository
from .repositories.mints import MintRepository
from .repositories.stakes import StakeRepository
from .repositories.swap import SwapRepository


class UnitOfWork:
    accounts: AccountRepository
    mints: MintRepository
    swaps: SwapRepository
    stakes: StakeRepository
        
    async def __aenter__(self):
        self.__session = AsyncSession(bind=async_engine,expire_on_commit=False)
        self.accounts = AccountRepository(self.__session)
        self.mints = MintRepository(self.__session)
        self.swaps = SwapRepository(self.__session)
        self.stakes = StakeRepository(self.__session)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e
        finally:
            await self.__session.close()