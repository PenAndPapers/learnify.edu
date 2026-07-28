from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field

from app.helpers.types import ValidDateOfBirth, ValidPassword, ValidPhoneNumber


class UserTypeEnum(StrEnum):
  ENROLLEE = "ENROLLEE"
  STUDENT = "STUDENT"
  EMPLOYEE = "EMPLOYEE"


class GenderEnum(StrEnum):
  MALE = "MALE"
  FEMALE = "FEMALE"
  OTHER = "OTHER"


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

  email: EmailStr = Field(..., examples=["johnny.smith@email.com"])
  password: ValidPassword = Field(..., examples=["P@s$w0rd_"])
  first_name: str = Field(..., min_length=1, max_length=100, examples=["Johnny"])
  last_name: str = Field(..., min_length=1, max_length=100, examples=["Smith"])
  phone_number: ValidPhoneNumber = Field(..., min_length=1, max_length=50, examples=["+123-2342-7890"])
  address: str = Field(..., min_length=1, max_length=250, examples=["99 Hanson Park 37th Street"])
  date_of_birth: ValidDateOfBirth = Field(..., examples=["2005-10-22"])
  gender: GenderEnum | None = None
  user_type: UserTypeEnum | None = None
  is_verified: bool = False

  model_config = {"from_attributes": True}


class UpdateUser(BaseModel):
  """The data required for updating a user"""

  email: EmailStr | None = Field(default=None, examples=["johnny.smith@email.com"])
  first_name: str | None = Field(default=None, min_length=1, max_length=100, examples=["Johnny"])
  last_name: str | None = Field(default=None, min_length=1, max_length=100, examples=["Smith"])
  phone_number: ValidPhoneNumber | None = Field(default=None, min_length=1, max_length=50, examples=["+123-2342-7890"])
  address: str | None = Field(default=None, min_length=1, max_length=250, examples=["99 Hanson Park 37th Street"])
  date_of_birth: ValidDateOfBirth | None = Field(default=None, examples=["2005-10-22"])
  gender: GenderEnum | None = None

  model_config = {"from_attributes": True}
