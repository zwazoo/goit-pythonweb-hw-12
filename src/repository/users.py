from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import User
from src.schemas.users import UserModelRegister
from src.services.users import get_gravatar_url


async def get_user_by_email(email: str, db: AsyncSession):
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(body: UserModelRegister, db: AsyncSession):
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
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def update_password(email: str, hashed_password: str, db: AsyncSession):
    user = await get_user_by_email(email, db)
    if user:
        user.hashed_password = hashed_password
        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def update_avatar(avatar_url: str, user_id: int, db: AsyncSession):
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
