from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from docfabric.db.tables import metadata


def create_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url)


async def init_db(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
