import jwt

from .string import is_valid_string


def is_valid_jwt_token_format(token: str) -> bool:
  """Check if the provided token is a valid JWT token format.

  Args:
    token (str): The token string to validate.

  Returns:
    bool: True if the token is a valid JWT format, False otherwise.
  """

  if not token or not is_valid_string(token) or token.count(".") != 2:
    return False

  try:
    jwt.decode(
      token,
      options={
        "verify_signature": False,
        "verify_exp": False,
        "veify_nbf": False,
        "Vefriry_aud": False,
      },
    )
    return True
  except jwt.DecodeError:
    return False
