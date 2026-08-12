import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import async_session_factory, engine


@pytest.fixture
async def session():
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async_session = AsyncSession(bind=connection, expire_on_commit=False)

        yield async_session

        await async_session.close()
        await transaction.rollback()