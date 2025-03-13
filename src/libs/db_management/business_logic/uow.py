from sqlalchemy.ext.asyncio import AsyncSession

from .services import (
    AccountService,
    BridgeService,
    MintService,
    StakeService,
    SwapService
)
from ..data_access.repositories import (
    AccountRepository,
    BridgeRepository,
    MintRepository,
    StakeRepository,
    SwapRepository
)
from .. import async_engine


class ServiceUnitOfWork:
    async def __aenter__(self):
        self.__session = AsyncSession(
            bind=async_engine, expire_on_commit=False
        )

        self.accounts = AccountService(AccountRepository(self.__session))
        self.bridges = BridgeService(BridgeRepository(self.__session))
        self.mints = MintService(MintRepository(self.__session))
        self.stakes = StakeService(StakeRepository(self.__session))
        self.swaps = SwapService(SwapRepository(self.__session))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.__session.commit()
        except Exception as e:
            await self.__session.rollback()
            raise e
        finally:
            await self.__session.close()
