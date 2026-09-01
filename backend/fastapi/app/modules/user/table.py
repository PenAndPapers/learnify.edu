from datetime import date
from uuid import uuid4

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.table import BaseTable

from .validation import GuardianTypeEnum, PreferredContactEnum, UserTypeEnum


class UserTable(BaseTable):
  __tablename__ = "users"

  uuid: Mapped[str] = mapped_column(String, default=lambda: str(uuid4()), unique=True)
  email: Mapped[str] = mapped_column(String, unique=True)
  password: Mapped[str] = mapped_column(String)
  first_name: Mapped[str] = mapped_column(String)
  last_name: Mapped[str] = mapped_column(String)

  # Nullable fields mapped cleanly with typing pipes
  phone_number: Mapped[str | None] = mapped_column(String)
  alternate_phone_number: Mapped[str | None] = mapped_column(String)
  gender: Mapped[str | None] = mapped_column(String)
  date_of_birth: Mapped[date | None] = mapped_column(Date)
  address: Mapped[str | None] = mapped_column(String)

  is_verified: Mapped[bool] = mapped_column(Boolean, server_default=false())

  # Polymorphism configuration
  user_type: Mapped[UserTypeEnum] = mapped_column(Enum(UserTypeEnum))

  # Modern 2.0 relationship typing
  guardians: Mapped[list["GuardianTable"]] = relationship(
    "GuardianTable", back_populates="user", cascade="all, delete-orphan"
  )
  tokens: Mapped[list["TokenTable"]] = relationship(
    "TokenTable", back_populates="user", cascade="all, delete-orphan"
  )

  __mapper_args__ = {"polymorphic_on": user_type, "polymorphic_identity": "user"}


class GuardianTable(BaseTable):
  __tablename__ = "guardians"

  user_id: Mapped[int] = mapped_column(
    Integer, ForeignKey("users.id"), primary_key=True
  )
  first_name: Mapped[str] = mapped_column(String)
  last_name: Mapped[str] = mapped_column(String)
  email: Mapped[str | None] = mapped_column(String, unique=True)
  phone_number: Mapped[str | None] = mapped_column(String)
  alternate_phone_number: Mapped[str | None] = mapped_column(String)
  address: Mapped[str | None] = mapped_column(String)
  occupation: Mapped[str | None] = mapped_column(String)
  relation_to_user: Mapped[GuardianTypeEnum] = mapped_column(Enum(GuardianTypeEnum))
  is_primary_contact: Mapped[bool] = mapped_column(Boolean, server_default=false())
  is_emergency_contact: Mapped[bool] = mapped_column(Boolean, server_default=false())
  preferred_contact_method: Mapped[PreferredContactEnum]

  # Modern 2.0 back-reference relationship mapping
  user: Mapped["UserTable"] = relationship("UserTable", back_populates="guardians")
