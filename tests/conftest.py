import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import engine


@pytest.fixture
async def session():
    async with engine.connect() as connection:
        transaction = await connection.begin()
        async_session = AsyncSession(bind=connection, expire_on_commit=False)

        yield async_session

        await async_session.close()
        await transaction.rollback()