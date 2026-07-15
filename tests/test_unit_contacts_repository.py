from datetime import date
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas.contacts import ContactModel
from src.repository.contacts import (
    get_contacts,
    get_contact_by_id,
    create_contact,
    update_contact,
    delete_contact,
)


def make_session():
    return AsyncMock(spec=AsyncSession)


def make_user():
    return User(id=1, username="testuser", email="test@example.com")


def make_contact():
    return Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+380991234567",
        birthdate=date(1990, 5, 15),
        user_id=1,
    )


def make_contact_body():
    return ContactModel(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="+380991234567",
        birthdate=date(1990, 5, 15),
    )


async def test_get_contacts():
    session = make_session()
    contact = make_contact()
    result = MagicMock()
    result.scalars.return_value.all.return_value = [contact]
    session.execute = AsyncMock(return_value=result)

    contacts = await get_contacts(session, user_id=1)

    assert len(contacts) == 1
    assert contacts[0].email == "john@example.com"


async def test_get_contact_by_id_found():
    session = make_session()
    contact = make_contact()
    result = MagicMock()
    result.scalar_one_or_none.return_value = contact
    session.execute = AsyncMock(return_value=result)

    found = await get_contact_by_id(contact_id=1, user_id=1, db=session)

    assert found is not None
    assert found.id == 1


async def test_get_contact_by_id_not_found():
    session = make_session()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    found = await get_contact_by_id(contact_id=99, user_id=1, db=session)

    assert found is None


async def test_create_contact():
    session = make_session()
    body = make_contact_body()

    result = await create_contact(body=body, user_id=1, db=session)

    assert result.first_name == "John"
    assert result.user_id == 1
    session.add.assert_called_once()
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once()


async def test_update_contact():
    session = make_session()
    contact = make_contact()
    result = MagicMock()
    result.scalar_one_or_none.return_value = contact
    session.execute = AsyncMock(return_value=result)

    body = ContactModel(
        first_name="Jane",
        last_name="Doe",
        email="john@example.com",
        phone="+380991234567",
        birthdate=date(1990, 5, 15),
    )
    updated = await update_contact(contact_id=1, body=body, user_id=1, db=session)

    assert updated.first_name == "Jane"
    session.commit.assert_awaited_once()


async def test_update_contact_not_found():
    session = make_session()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    updated = await update_contact(
        contact_id=99, body=make_contact_body(), user_id=1, db=session
    )

    assert updated is None


async def test_delete_contact():
    session = make_session()
    contact = make_contact()
    result = MagicMock()
    result.scalar_one_or_none.return_value = contact
    session.execute = AsyncMock(return_value=result)

    deleted = await delete_contact(contact_id=1, user_id=1, db=session)

    assert deleted is not None
    session.delete.assert_awaited_once_with(contact)
    session.commit.assert_awaited_once()


async def test_delete_contact_not_found():
    session = make_session()
    result = MagicMock()
    result.scalar_one_or_none.return_value = None
    session.execute = AsyncMock(return_value=result)

    deleted = await delete_contact(contact_id=99, user_id=1, db=session)

    assert deleted is None
