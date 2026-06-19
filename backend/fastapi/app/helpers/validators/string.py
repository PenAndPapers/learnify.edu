def is_valid_string(value: str) -> bool:
  """Check if the provided value is a valid non-empty string."""
  return isinstance(value, str) and len(value.strip()) > 0
