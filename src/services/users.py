import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from libgravatar import Gravatar

from src.config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
)


def get_gravatar_url(email: str) -> str:
    return Gravatar(email).get_image(size=200, default="identicon")


async def upload_avatar(file: UploadFile, user_id: int) -> str:
    result = cloudinary.uploader.upload(
        file.file,
        public_id=f"avatars/user_{user_id}",
        overwrite=True,
        crop="fill",
        width=200,
        height=200,
    )
    return result["secure_url"]
