from typing import List
from fastapi import Depends, HTTPException, status, Request

from src.database import User, Role
from src.services.auth import get_current_user


class RoleAccess:
    def __init__(self, allowed_roles: List[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, request: Request, current_user: User = Depends(get_current_user)
    ):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
