import re
from typing import Annotated

from annotated_types import MinLen
from passlib.context import CryptContext
from pydantic.functional_validators import AfterValidator

from app.core.validation import NonEmptyStr
from app.helpers.validators import is_valid_string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def is_valid_password(password: NonEmptyStr) -> bool:
  pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[_@$#%&*]).+$"

  if not re.match(pattern, password):
    raise ValueError("Password must contain at least one uppercase letter, one lowercase letter, one digit, and one special character (_@$#%&*).")

  return bool(re.match(pattern, password))

def hash_password(password: NonEmptyStr) -> str:
  """Hash a password using bcrypt algorithm."""
  if not is_valid_string(password):
    raise ValueError("Password must be a non-empty string.")

  return pwd_context.hash(password)


def verify_password(plain_password: NonEmptyStr, hashed_password: NonEmptyStr) -> bool:
  """Verify a plain password against a hashed password."""
  if not is_valid_string(plain_password) or not is_valid_string(hashed_password):
    raise ValueError("Passwords must be non-empty strings.")
  return pwd_context.verify(plain_password, hashed_password)

ValidPassword = Annotated[str, MinLen(8), AfterValidator(is_valid_password)]
