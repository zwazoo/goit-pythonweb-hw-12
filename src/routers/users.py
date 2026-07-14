from fastapi import APIRouter, Depends, Request, UploadFile, File
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.database import get_db
from src.database.models import User
from src.schemas.users import UserModel
from src.repository import users
from src.services.auth import get_current_user
from src.services.users import upload_avatar

router = APIRouter(
    prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)]
)
limiter = Limiter(key_func=get_remote_address)


@router.get("/me", response_model=UserModel, description="No more than 3 requests per minute")
@limiter.limit("3/minute")
async def me(request: Request, current_user: User = Depends(get_current_user)):
    return current_user


@router.patch("/avatar", response_model=UserModel, operation_id="update_avatar")
async def update_avatar(
    file: UploadFile = File(),
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    avatar_url = await upload_avatar(file, current_user.id)
    return await users.update_avatar(avatar_url, current_user.id, db)
