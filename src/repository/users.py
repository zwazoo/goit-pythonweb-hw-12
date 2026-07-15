from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import User
from src.schemas.users import UserModelRegister
from src.services.users import get_gravatar_url


async def get_user_by_email(email: str, db: AsyncSession):
    """Return a user by email address.

    Args:
        email: Email address to search for.
        db: Async database session.

    Returns:
        User instance if found, None otherwise.
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(body: UserModelRegister, db: AsyncSession):
    """Create a new user with a Gravatar avatar and persist to the database.

    Args:
        body: Registration data containing username, email and hashed password.
        db: Async database session.

    Returns:
        Newly created User instance.

    Raises:
        Exception: Rolls back and re-raises if the commit fails.
    """
    user = User(
        username=body.username,
        email=body.email,
        hashed_password=body.password,
        avatar=get_gravatar_url(body.email),
    )
    db.add(user)
    try:
        await db.commit()
        await db.refresh(user)
    except Exception:
        await db.rollback()
        raise
    return user


async def change_confirmed_email(email: str, db: AsyncSession):
    """Mark a user's email as confirmed.

    Args:
        email: Email address of the user to confirm.
        db: Async database session.

    Raises:
        Exception: Rolls back and re-raises if the commit fails.
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def update_password(email: str, hashed_password: str, db: AsyncSession):
    """Update the hashed password for a user identified by email.

    Args:
        email: Email address of the user.
        hashed_password: New Argon2 password hash to store.
        db: Async database session.

    Raises:
        Exception: Rolls back and re-raises if the commit fails.
    """
    user = await get_user_by_email(email, db)
    if user:
        user.hashed_password = hashed_password
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def update_avatar(avatar_url: str, user_id: int, db: AsyncSession):
    """Update the avatar URL for a user identified by ID.

    Args:
        avatar_url: Public URL of the uploaded avatar image.
        user_id: ID of the user to update.
        db: Async database session.

    Returns:
        Updated User instance, or None if the user was not found.

    Raises:
        Exception: Rolls back and re-raises if the commit fails.
    """
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user:
        user.avatar = avatar_url
        try:
            await db.commit()
            await db.refresh(user)
        except Exception:
            await db.rollback()
            raise
    return user
