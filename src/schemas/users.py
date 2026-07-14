from typing import Optional
from pydantic import BaseModel, EmailStr


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserModelRegister(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserModel(BaseModel):
    username: str
    email: EmailStr
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    avatar: str


class RequestEmail(BaseModel):
    email: EmailStr


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
