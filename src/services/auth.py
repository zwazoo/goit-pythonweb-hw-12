from datetime import datetime, timezone, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from pwdlib import PasswordHash

from src.database import get_db
from src.repository.users import get_user_by_email
from src.config import settings

_password_hash = PasswordHash.recommended()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return _password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return _password_hash.hash(password)


async def create_access_token(data: dict, expires_delta: int = 3600) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(
        to_encode, settings.hash_secret, algorithm=settings.hash_algorithm
    )


async def create_refresh_token(data: dict, expires_delta: int = 7 * 24 * 3600) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(
        to_encode, settings.hash_secret, algorithm=settings.hash_algorithm
    )


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token.credentials,
            settings.hash_secret,
            algorithms=[settings.hash_algorithm],
        )
        if payload.get("token_type") != "access":
            raise credentials_exception
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await get_user_by_email(email, db)
    if user is None:
        raise credentials_exception
    return user


def create_email_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update(
        {"iat": datetime.now(timezone.utc), "exp": expire, "token_type": "email_token"}
    )
    return jwt.encode(
        to_encode, settings.hash_secret, algorithm=settings.hash_algorithm
    )


def get_email_from_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.hash_secret, algorithms=[settings.hash_algorithm]
        )
        if payload.get("token_type") != "email_token":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification",
        )
