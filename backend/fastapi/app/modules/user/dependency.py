from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from .repository import EnrolleeResitory, UserRepository
from .service import EnrolleeService, UserService


# User service dependency
def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
  return UserRepository(db)


def get_user_service(repository: UserRepository = Depends(get_user_repository)) -> UserService:
  return UserService(repository)


# Enrollee service dependency
def get_enrollee_repository(db: Session = Depends(get_db)) -> EnrolleeResitory:
  return EnrolleeResitory(db)


def get_enrolle_service(
  repository: EnrolleeResitory = Depends(get_enrollee_repository),
) -> EnrolleeService:
  return EnrolleeService(repository)
