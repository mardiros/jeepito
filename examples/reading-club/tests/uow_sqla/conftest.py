from typing import AsyncIterator

import pytest
from reading_club.adapters.uow_sqla import orm
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

DATABASE_URL = "sqlite+aiosqlite:///"


@pytest.fixture
def bared_sqla_engine() -> AsyncEngine:
    engine = create_async_engine(DATABASE_URL, future=True, echo=False)
    return engine


@pytest.fixture
async def sqla_engine(
    bared_sqla_engine: AsyncEngine,
) -> AsyncIterator[AsyncEngine]:
    async with bared_sqla_engine.begin() as conn:
        await conn.run_sync(orm.metadata.create_all)

    yield bared_sqla_engine

    async with bared_sqla_engine.begin() as conn:
        await conn.run_sync(orm.metadata.drop_all)


@pytest.fixture()
def sqla_session(sqla_engine: AsyncEngine) -> AsyncSession:
    async_session = async_sessionmaker(sqla_engine, class_=AsyncSession)
    return async_session()
