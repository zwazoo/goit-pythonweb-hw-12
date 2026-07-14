from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from src.config import settings

DB_URL = f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}@{settings.db_domain}:{settings.db_port}/{settings.db_name}"

engine = create_async_engine(DB_URL)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
