from datetime import date
from sqlalchemy import Date, String
from sqlalchemy.sql.schema import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .connection import Base


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("email", "user_id", name="unique_user_contact"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False)
    birthdate: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    user: Mapped["User"] = relationship(backref="contacts")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    hashed_password: Mapped[str] = mapped_column(String(128), nullable=False)
    avatar: Mapped[str | None] = mapped_column(String(255), nullable=True)
    confirmed: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)
