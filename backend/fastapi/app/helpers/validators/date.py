
from datetime import date


def is_birth_date_valid_to_register(value: date | None) -> bool:
  """Check if the provided date of birth is valid for registration. The user must be at least 10 years old and the date of birth cannot be in the future or before January 1, 1900."""

  if value is None:
      return value

  today = date.today()

  if value > today or value < date(1900, 1, 1):
    return False

  # Robust age calculation accounts for months and days perfectly
  age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
  if age < 10:
    return False

  return True
