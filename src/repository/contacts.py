from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import Contact
from src.schemas.contacts import ContactModel


async def get_contacts(
    db: AsyncSession,
    user_id: int,
    first_name: str | None = None,
    last_name: str | None = None,
    email: str | None = None,
):
    """Return all contacts for a user with optional case-insensitive filters.

    Args:
        db: Async database session.
        user_id: ID of the owner user.
        first_name: Filter by first name substring (optional).
        last_name: Filter by last name substring (optional).
        email: Filter by email substring (optional).

    Returns:
        List of matching Contact instances.
    """
    stmt = select(Contact).where(Contact.user_id == user_id)
    if first_name:
        stmt = stmt.where(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        stmt = stmt.where(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        stmt = stmt.where(Contact.email.ilike(f"%{email}%"))
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_contact_by_id(contact_id: int, user_id: int, db: AsyncSession):
    """Return a single contact by ID scoped to the given user.

    Args:
        contact_id: ID of the contact to retrieve.
        user_id: ID of the owner user.
        db: Async database session.

    Returns:
        Contact instance if found, None otherwise.
    """
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_contact(body: ContactModel, user_id: int, db: AsyncSession):
    """Create a new contact for a user and persist to the database.

    Args:
        body: Contact data from the request.
        user_id: ID of the owner user.
        db: Async database session.

    Returns:
        Newly created Contact instance.

    Raises:
        Exception: Rolls back and re-raises if the commit fails.
    """
    contact = Contact(**body.model_dump(), user_id=user_id)
    db.add(contact)
    try:
        await db.commit()
        await db.refresh(contact)
    except Exception:
        await db.rollback()
        raise
    return contact


async def update_contact(
    contact_id: int, body: ContactModel, user_id: int, db: AsyncSession
):
    """Update an existing contact's data.

    Args:
        contact_id: ID of the contact to update.
        body: New contact data from the request.
        user_id: ID of the owner user.
        db: Async database session.

    Returns:
        Updated Contact instance, or None if the contact was not found.

    Raises:
        Exception: Rolls back and re-raises if the commit fails.
    """
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
    )
    contact = result.scalar_one_or_none()
    if contact:
        for key, value in body.model_dump().items():
            setattr(contact, key, value)
        try:
            await db.commit()
            await db.refresh(contact)
        except Exception:
            await db.rollback()
            raise
    return contact


async def delete_contact(contact_id: int, user_id: int, db: AsyncSession):
    """Delete a contact and return it.

    Args:
        contact_id: ID of the contact to delete.
        user_id: ID of the owner user.
        db: Async database session.

    Returns:
        Deleted Contact instance, or None if the contact was not found.

    Raises:
        Exception: Rolls back and re-raises if the commit fails.
    """
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
    )
    contact = result.scalar_one_or_none()
    if contact:
        try:
            await db.delete(contact)
            await db.commit()
        except Exception:
            await db.rollback()
            raise
    return contact
