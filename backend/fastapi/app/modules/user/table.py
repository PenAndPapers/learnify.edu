from uuid import uuid4

from sqlalchemy import Boolean, Column, Date, String, false
from sqlalchemy.orm import relationship

from app.core.base_model import AppBaseModel


class UserTable(AppBaseModel):
  """
  The Single Source of Truth for Identity & Core Biography.
  Every human in the system has a row here.
  """

  __tablename__ = "users"

  uuid = Column(String, default=lambda: str(uuid4()), unique=True, nullable=False)
  email = Column(String, unique=True, nullable=False)
  password = Column(String, nullable=False)
  first_name = Column(String, nullable=False)
  last_name = Column(String, nullable=False)
  phone_number = Column(String, nullable=True)
  gender = Column(String, nullable=True)
  date_of_birth = Column(Date, nullable=True)
  address = Column(String, nullable=True)
  is_verified = Column(Boolean, server_default=false(), nullable=False)

  # Polymorphism
  user_type = Column(String, nullable=False)

  tokens = relationship(
    "TokenTable", back_populates="user", cascade="all, delete-orphan"
  )

  __mapper_args__ = {"polymorphic_on": user_type, "polymorphic_identity": "user"}
