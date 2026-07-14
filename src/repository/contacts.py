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
    result = await db.execute(
        select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def create_contact(body: ContactModel, user_id: int, db: AsyncSession):
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
