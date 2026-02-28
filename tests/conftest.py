import pytest
from sqlalchemy.ext.asyncio import AsyncEngine

from docfabric.db.engine import create_engine, init_db


@pytest.fixture
async def engine() -> AsyncEngine:
    eng = create_engine("sqlite+aiosqlite://")
    await init_db(eng)
    yield eng
    await eng.dispose()
