def is_valid_string(value: str) -> bool:
  """Check if the provided value is a valid non-empty string."""
  return isinstance(value, str) and len(value.strip()) > 0


def is_valid_phone_number(value: str) -> bool:
  """Check if the provided value is a valid phone number format. Accepted special characters are +, -, (, ), and space. The phone number must contain at least 7 digits and can start with a + for country code."""
  import re

  if not is_valid_string(value):
    return False

  # Remove accepted special characters and check if the remaining string contains only digits
  pattern = r"^\+?[\d\s\-\(\)]{7,}$"

  if not re.match(pattern, value):
    return False

  return True

