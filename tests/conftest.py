import asyncio
from unittest.mock import MagicMock, patch

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from main import app
from src.database.models import Base, User, Role
from src.database import get_db
from src.services.auth import create_access_token, get_password_hash
from src.config import settings

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+asyncpg://{settings.db_user}:{settings.db_password}"
    f"@localhost:{settings.db_port}/{settings.db_name}_test"
)

engine = create_async_engine(SQLALCHEMY_DATABASE_URL, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, expire_on_commit=False, bind=engine
)

test_user = {
    "username": "testuser",
    "email": "user@example.com",
    "password": "12345678",
}


@pytest.fixture(scope="module", autouse=True)
def init_models_wrap():
    async def init_models():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        async with TestingSessionLocal() as session:
            current_user = User(
                username=test_user["username"],
                email=test_user["email"],
                hashed_password=get_password_hash(test_user["password"]),
                confirmed=True,
                avatar="https://gravatar.com/avatar",
                role=Role.user,
            )
            session.add(current_user)
            await session.commit()

    asyncio.run(init_models())


@pytest.fixture(scope="module")
def client():
    async def override_get_db():
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db

    mock_redis = MagicMock()
    mock_redis.get.return_value = None  # always miss cache → fetch from test DB

    with patch("src.services.auth.r", mock_redis):
        yield TestClient(app)


@pytest_asyncio.fixture()
async def get_token():
    token = await create_access_token(data={"sub": test_user["email"]})
    return token
