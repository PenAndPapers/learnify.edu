from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.helpers.validators.date import is_birth_date_valid_to_register
from app.helpers.validators.string import is_valid_phone_number


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
  password: str = Field(..., min_length=8, examples=["P@s$w0rd_"])
  first_name: str = Field(..., min_length=1, max_length=100, examples=["Johnny"])
  last_name: str = Field(..., min_length=1, max_length=100, examples=["Smith"])
  phone_number: str = Field(..., min_length=1, max_length=50, examples=["+123-2342-7890"])
  address: str = Field(..., min_length=1, max_length=250, examples=["99 Hanson Park 37th Street"])
  date_of_birth: date | None = Field(..., examples=["2005-10-22"])
  gender: GenderEnum | None = None
  user_type: UserTypeEnum | None = None
  is_verified: bool = False

  @field_validator("date_of_birth")
  @classmethod
  def validate_date_of_birth(cls, value: date | None) -> date | None:
    if not is_birth_date_valid_to_register(value):
      raise ValueError(
        "Invalid date of birth. User must be at least 10 years old and the date of birth cannot be in the future or before January 1, 1900."
      )
    return value

  @field_validator("phone_number")
  @classmethod
  def validate_phone_number(cls, value: str) -> str:
    if not is_valid_phone_number(value):
      raise ValueError(
        "Invalid phone number format. Accepted special characters are +, -, (, ), and space. The phone number must contain at least 7 digits and can start with a + for country code."
      )
    return value
