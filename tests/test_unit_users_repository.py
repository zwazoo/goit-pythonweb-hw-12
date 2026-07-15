from unittest.mock import AsyncMock, MagicMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User, Role
from src.schemas.users import UserModelRegister
from src.repository.users import (
    get_user_by_email,
    create_user,
    change_confirmed_email,
    update_password,
    update_avatar,
)


def make_session():
    return AsyncMock(spec=AsyncSession)


def make_user(**kwargs):
    defaults = dict(
        id=1,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        confirmed=False,
        avatar="https://gravatar.com/avatar",
        role=Role.user,
    )
    return User(**{**defaults, **kwargs})


async def test_get_user_by_email_found():
    session = make_session()
    user = make_user()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)

    found = await get_user_by_email("test@example.com", session)

    assert found is not None
    assert found.email == "test@example.com"


async def test_get_user_by_email_not_found():
    session = make_session()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    found = await get_user_by_email("nobody@example.com", session)

    assert found is None


async def test_create_user():
    session = make_session()
    body = UserModelRegister(
        username="newuser", email="new@example.com", password="hashed_pw"
    )

    with patch(
        "src.repository.users.get_gravatar_url",
        return_value="https://gravatar.com/avatar",
    ):
        user = await create_user(body, session)

    assert user.username == "newuser"
    assert user.email == "new@example.com"
    assert user.avatar == "https://gravatar.com/avatar"
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


async def test_create_user_db_error():
    session = make_session()
    session.commit = AsyncMock(side_effect=Exception("DB error"))
    body = UserModelRegister(username="u", email="u@example.com", password="pw")

    with patch("src.repository.users.get_gravatar_url", return_value=""):
        try:
            await create_user(body, session)
        except Exception:
            pass

    session.rollback.assert_awaited_once()


async def test_change_confirmed_email():
    session = make_session()
    user = make_user(confirmed=False)
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)

    await change_confirmed_email("test@example.com", session)

    assert user.confirmed is True
    session.commit.assert_awaited_once()


async def test_change_confirmed_email_user_not_found():
    session = make_session()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    await change_confirmed_email("nobody@example.com", session)

    session.commit.assert_not_awaited()


async def test_change_confirmed_email_db_error():
    session = make_session()
    user = make_user(confirmed=False)
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock(side_effect=Exception("DB error"))

    try:
        await change_confirmed_email("test@example.com", session)
    except Exception:
        pass

    session.rollback.assert_awaited_once()


async def test_update_password():
    session = make_session()
    user = make_user()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)

    await update_password("test@example.com", "new_hashed_pw", session)

    assert user.hashed_password == "new_hashed_pw"
    session.commit.assert_awaited_once()


async def test_update_password_user_not_found():
    session = make_session()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    await update_password("nobody@example.com", "new_hashed_pw", session)

    session.commit.assert_not_awaited()


async def test_update_password_db_error():
    session = make_session()
    user = make_user()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock(side_effect=Exception("DB error"))

    try:
        await update_password("test@example.com", "new_pw", session)
    except Exception:
        pass

    session.rollback.assert_awaited_once()


async def test_update_avatar():
    session = make_session()
    user = make_user()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)

    updated = await update_avatar(
        "https://new-avatar.com/img.jpg", user_id=1, db=session
    )

    assert updated.avatar == "https://new-avatar.com/img.jpg"
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


async def test_update_avatar_db_error():
    session = make_session()
    user = make_user()
    result = MagicMock()
    result.scalar_one_or_none.return_value = user
    session.execute = AsyncMock(return_value=result)
    session.commit = AsyncMock(side_effect=Exception("DB error"))

    try:
        await update_avatar("https://new-avatar.com/img.jpg", user_id=1, db=session)
    except Exception:
        pass

    session.rollback.assert_awaited_once()


async def test_update_avatar_user_not_found():
    session = make_session()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    updated = await update_avatar(
        "https://new-avatar.com/img.jpg", user_id=99, db=session
    )

    assert updated is None
