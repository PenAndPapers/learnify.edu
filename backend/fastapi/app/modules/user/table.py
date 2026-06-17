from datetime import date
from uuid import uuid4

from sqlalchemy import Boolean, Date, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.table import BaseTable


class UserTable(BaseTable):
  __tablename__ = "users"

  uuid: Mapped[str] = mapped_column(String, default=lambda: str(uuid4()), unique=True)
  email: Mapped[str] = mapped_column(String, unique=True)
  password: Mapped[str] = mapped_column(String)
  first_name: Mapped[str] = mapped_column(String)
  last_name: Mapped[str] = mapped_column(String)

  # Nullable fields mapped cleanly with typing pipes
  phone_number: Mapped[str | None] = mapped_column(String)
  gender: Mapped[str | None] = mapped_column(String)
  date_of_birth: Mapped[date | None] = mapped_column(Date)
  address: Mapped[str | None] = mapped_column(String)

  is_verified: Mapped[bool] = mapped_column(Boolean, server_default=false())

  # Polymorphism configuration
  user_type: Mapped[str] = mapped_column(String)

  # Modern 2.0 relationship typing
  tokens: Mapped[list["TokenTable"]] = relationship(
    "TokenTable", back_populates="user", cascade="all, delete-orphan"
  )

  __mapper_args__ = {"polymorphic_on": user_type, "polymorphic_identity": "user"}
