from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field


class UserTypeEnum(StrEnum):
  ENROLLEE = "ENROLLEE"
  STUDENT = "STUDENT"
  EMPLOYEE = "EMPLOYEE"


class UserBaseResponse(BaseModel):
  """User schema containing shared details"""

  uuid: str
  email: EmailStr
  first_name: str | None = None
  last_name: str | None = None
  phone_number: str | None = None
  gender: str | None = None
  date_of_birth: date | None = None
  address: str | None = None
  user_type: UserTypeEnum
  created_at: datetime
  updated_at: datetime
  deleted_at: datetime | None = None

  model_config = {"from_attributes": True}


class UserInternalResponse(UserBaseResponse):
  """
  User schema containing sensitive user details
  Note:
    Avoid using this for returning a response
  """

  id: int

  model_config = {"from_attributes": True}


class CreateUser(BaseModel):
  """The data required for creating a user"""

  email: EmailStr
  password: str = Field(..., min_length=8)
  first_name: str | None = Field(default=None, max_length=100)
  last_name: str | None = Field(default=None, max_length=100)
  phone_number: str | None = Field(default=None, max_length=50)
  gender: str | None = Field(default=None, max_length=50)
  date_of_birth: date | None = None
  address: str | None = Field(default=None, max_length=250)
  is_verified: bool = Field(default=False)
  user_type: UserTypeEnum | None = Field(default=None)
