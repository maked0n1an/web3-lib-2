from sqlalchemy.ext.asyncio import AsyncSession

from .db_init import async_engine
from .implementations import AccountRepository


class UnitOfWork:
    accounts: AccountRepository
        
    async def __aenter__(self):
        self.__session = AsyncSession(bind=async_engine)
        self.accounts = AccountRepository(self.__session)
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e
        finally:
            await self.__session.close()