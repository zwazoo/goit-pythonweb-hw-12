from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr


class ContactModel(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str
    birthdate: date
    notes: Optional[str] = None


class ContactResponse(ContactModel):
    id: int

    class Config:
        from_attributes = True


class BirthdayResponse(BaseModel):
    id: int
    name: str
    congratulation_date: date
