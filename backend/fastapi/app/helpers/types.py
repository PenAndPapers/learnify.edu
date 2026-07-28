from annotated_types import MinLen
from datetime import date
from typing import Annotated
from pydantic import Field, StringConstraints
from pydantic.functional_validators import AfterValidator

from .security.password import is_valid_password
from .validators.date import validate_date_of_birth
from .validators.string import validate_phone_number

# Define custom types
NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
PositiveInt = Annotated[int, Field(gt=0)]
ValidPassword = Annotated[str, MinLen(8), AfterValidator(is_valid_password)]
ValidDateOfBirth = Annotated[date | None, AfterValidator(validate_date_of_birth)]
ValidPhoneNumber = Annotated[str | None, AfterValidator(validate_phone_number)]