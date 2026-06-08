from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
  if not password:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, detail="Password must not be empty"
    )
  return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
  if not plain_password or not hashed_password:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST, detail="Password must not be empty"
    )
  return pwd_context.verify(plain_password, hashed_password)
