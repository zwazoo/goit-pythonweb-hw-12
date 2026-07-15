from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
    Form,
)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
import jwt

from src.database import get_db
from src.schemas.users import (
    UserModel,
    UserModelRegister,
    UserLoginRequest,
    Token,
    RequestEmail,
)
from src.repository import users as repository_users
from src.repository.users import change_confirmed_email
from src.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    get_email_from_token,
    get_email_from_reset_token,
)
from src.services.email import send_email, send_reset_password_email
from src.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
templates = Jinja2Templates(
    directory=Path(__file__).parent.parent / "services" / "templates"
)


@router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserModelRegister,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Account already exists"
        )
    body.password = get_password_hash(body.password)
    user = await repository_users.create_user(body, db)

    background_tasks.add_task(
        send_email, user.email, user.username, str(request.base_url)
    )
    return user


@router.post("/login", response_model=Token)
async def login(body: UserLoginRequest, db: AsyncSession = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email"
        )
    if not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not confirmed"
        )
    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db: AsyncSession = Depends(get_db),
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.hash_secret,
            algorithms=[settings.hash_algorithm],
        )
        if payload.get("token_type") != "refresh":
            raise credentials_exception
        email: str | None = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise credentials_exception

    access_token = await create_access_token(data={"sub": user.email})
    new_refresh = await create_refresh_token(data={"sub": user.email})
    return {
        "access_token": access_token,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(token: str, db: AsyncSession = Depends(get_db)):
    email = get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error"
        )
    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    await change_confirmed_email(email, db)
    return {"message": "Email confirmed"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        if user.confirmed:
            return {"message": "Your email is already confirmed"}
        background_tasks.add_task(
            send_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "Check your email for confirmation."}


@router.post("/forgot_password")
async def forgot_password(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user and user.confirmed:
        background_tasks.add_task(
            send_reset_password_email, user.email, user.username, str(request.base_url)
        )
    return {"message": "You will receive a password reset link."}


@router.get("/reset_password/{token}", response_class=HTMLResponse)
async def reset_password_form(token: str, request: Request):
    get_email_from_reset_token(token)
    return templates.TemplateResponse(
        request=request, name="reset_password_form.html", context={"token": token}
    )


@router.post("/reset_password/{token}")
async def reset_password(
    token: str,
    password: str = Form(),
    db: AsyncSession = Depends(get_db),
):
    email = get_email_from_reset_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User not found"
        )
    await repository_users.update_password(email, get_password_hash(password), db)
    return {"message": "Password updated successfully"}
