from typing import Annotated

from pydantic import Field, StringConstraints

# Define a non-empty string type
NonEmptyStr = Annotated[str, StringConstraints(min_length=1, strip_whitespace=True)]
PositiveInt = Annotated[int, Field(gt=0)]
