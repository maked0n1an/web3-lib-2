import asyncio

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from .core.entities import BaseSqlModel


DATABASE_URL = 'sqlite+aiosqlite:///./user_data/wallets.db'

async_engine = create_async_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    echo=False,
    future=True
)
async_session_maker = async_sessionmaker(
    async_engine,
    # expire_on_commit=False
)


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(BaseSqlModel.metadata.create_all)

asyncio.run(init_models())