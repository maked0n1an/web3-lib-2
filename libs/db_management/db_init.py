import asyncio

from sqlalchemy.ext.asyncio import create_async_engine

from .models import SqlBaseModel

async_engine = create_async_engine(
    'sqlite+aiosqlite:///./wallets.db',
    pool_pre_ping=True,
    echo=True,
    future=True
)

async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(SqlBaseModel.metadata.create_all)

asyncio.run(init_models())