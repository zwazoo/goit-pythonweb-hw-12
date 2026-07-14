from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError

from src.repository import contacts
from src.services.auth import get_current_user
from src.services import contacts as contacts_service
from src.database import get_db
from src.database.models import User
from src.schemas.contacts import ContactModel, ContactResponse, BirthdayResponse

router = APIRouter(
    prefix="/contacts", tags=["contacts"], dependencies=[Depends(get_current_user)]
)


@router.get(
    "/birthdays",
    response_model=list[BirthdayResponse],
    name="Get contacts with upcoming birthdays",
)
async def get_upcoming_birthdays(
    current_user: User = Depends(get_current_user), db=Depends(get_db)
):
    all_contacts = await contacts.get_contacts(db, current_user.id)
    return contacts_service.get_upcoming_birthdays(all_contacts)


@router.get("/", response_model=list[ContactResponse], name="Get all contacts")
async def get_contacts(
    first_name: Annotated[
        str | None, Query(description="Search contacts by first name", min_length=1)
    ] = None,
    last_name: Annotated[
        str | None, Query(description="Search contacts by last name", min_length=1)
    ] = None,
    email: Annotated[
        str | None, Query(description="Search contacts by email", min_length=1)
    ] = None,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    return await contacts.get_contacts(
        db, current_user.id, first_name, last_name, email
    )


@router.post(
    "/",
    response_model=ContactResponse,
    name="Create new contact",
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    body: ContactModel,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        return await contacts.create_contact(body, current_user.id, db)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )


@router.get("/{contact_id}", response_model=ContactResponse, name="Get contact by ID")
async def get_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    contact = await contacts.get_contact_by_id(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.put(
    "/{contact_id}", response_model=ContactResponse, name="Update contact by ID"
)
async def update_contact(
    contact_id: int,
    body: ContactModel,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    try:
        contact = await contacts.update_contact(contact_id, body, current_user.id, db)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact


@router.delete(
    "/{contact_id}", response_model=ContactResponse, name="Delete contact by ID"
)
async def delete_contact(
    contact_id: int,
    current_user: User = Depends(get_current_user),
    db=Depends(get_db),
):
    contact = await contacts.delete_contact(contact_id, current_user.id, db)
    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found"
        )
    return contact
