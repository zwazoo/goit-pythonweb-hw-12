from typing import List
from fastapi import Depends, HTTPException, status, Request

from src.database import User, Role
from src.services.auth import get_current_user


class RoleAccess:
    """FastAPI dependency that restricts access to users with allowed roles.

    Args:
        allowed_roles: List of roles permitted to access the endpoint.
    """

    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, request: Request, current_user: User = Depends(get_current_user)
    ):
        """Check that the current user has one of the allowed roles.

        Args:
            request: Incoming HTTP request.
            current_user: Authenticated user resolved by get_current_user.

        Raises:
            HTTPException: 403 if the user's role is not in allowed_roles.
        """
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
