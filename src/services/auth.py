import redis
import pickle
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

r = redis.Redis(host="redis", port=6379, db=0)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against its Argon2 hash.

    Args:
        plain_password: The raw password provided by the user.
        hashed_password: The stored Argon2 hash to compare against.

    Returns:
        True if the password matches, False otherwise.
    """
    return _password_hash.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a plain password using Argon2.

    Args:
        password: The raw password to hash.

    Returns:
        Argon2 hash string.
    """
    return _password_hash.hash(password)


async def create_access_token(data: dict, expires_delta: int = 3600) -> str:
    """Create a signed JWT access token.

    Args:
        data: Payload to encode (must include ``sub`` with user email).
        expires_delta: Token lifetime in seconds. Defaults to 3600.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(
        to_encode, settings.hash_secret, algorithm=settings.hash_algorithm
    )


async def create_refresh_token(data: dict, expires_delta: int = 7 * 24 * 3600) -> str:
    """Create a signed JWT refresh token.

    Args:
        data: Payload to encode (must include ``sub`` with user email).
        expires_delta: Token lifetime in seconds. Defaults to 7 days.

    Returns:
        Encoded JWT string.
    """
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
    """Decode the Bearer token and return the authenticated user.

    Checks Redis cache first; falls back to the database and caches the result
    for 900 seconds.

    Args:
        token: Bearer credentials extracted from the Authorization header.
        db: Async database session.

    Returns:
        Authenticated User instance.

    Raises:
        HTTPException: 401 if the token is invalid or the user does not exist.
    """
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

    user = r.get(f"user:{email}")
    if user is None:
        user = await get_user_by_email(email, db)
        if user is None:
            raise credentials_exception
        r.set(f"user:{email}", pickle.dumps(user))
        r.expire(f"user:{email}", 900)
    else:
        user = pickle.loads(user)

    return user


def create_password_reset_token(email: str) -> str:
    """Create a signed JWT token for password reset.

    Args:
        email: Email address of the user requesting the reset.

    Returns:
        Encoded JWT string valid for 1 hour.
    """
    data = {"sub": email}
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    data.update(
        {
            "iat": datetime.now(timezone.utc),
            "exp": expire,
            "token_type": "reset_password",
        }
    )
    return jwt.encode(data, settings.hash_secret, algorithm=settings.hash_algorithm)


def get_email_from_reset_token(token: str) -> str:
    """Decode a password reset token and return the email address.

    Args:
        token: Encoded JWT password reset token.

    Returns:
        Email address extracted from the token payload.

    Raises:
        HTTPException: 401 if the token type is wrong.
        HTTPException: 422 if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(
            token, settings.hash_secret, algorithms=[settings.hash_algorithm]
        )
        if payload.get("token_type") != "reset_password":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type"
            )
        return payload["sub"]
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid password reset token",
        )


def create_email_token(data: dict) -> str:
    """Create a signed JWT token for email verification.

    Args:
        data: Payload to encode (must include ``sub`` with user email).

    Returns:
        Encoded JWT string valid for 1 hour.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(hours=1)
    to_encode.update(
        {"iat": datetime.now(timezone.utc), "exp": expire, "token_type": "email_token"}
    )
    return jwt.encode(
        to_encode, settings.hash_secret, algorithm=settings.hash_algorithm
    )


def get_email_from_token(token: str) -> str:
    """Decode an email verification token and return the email address.

    Args:
        token: Encoded JWT email verification token.

    Returns:
        Email address extracted from the token payload.

    Raises:
        HTTPException: 401 if the token type is wrong.
        HTTPException: 422 if the token is invalid or expired.
    """
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
