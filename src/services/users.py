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
    """Return a Gravatar URL for the given email address.

    Args:
        email: User's email address.

    Returns:
        URL string of the 200x200 Gravatar image with identicon fallback.
    """
    return Gravatar(email).get_image(size=200, default="identicon")


async def upload_avatar(file: UploadFile, user_id: int) -> str:
    """Upload an avatar image to Cloudinary and return its secure URL.

    The image is cropped and resized to 200x200 pixels. The public ID is
    deterministic, so re-uploading replaces the previous avatar.

    Args:
        file: Uploaded image file from the request.
        user_id: ID of the user, used as part of the Cloudinary public ID.

    Returns:
        Secure HTTPS URL of the uploaded avatar.
    """
    result = cloudinary.uploader.upload(
        file.file,
        public_id=f"avatars/user_{user_id}",
        overwrite=True,
        crop="fill",
        width=200,
        height=200,
    )
    return result["secure_url"]
