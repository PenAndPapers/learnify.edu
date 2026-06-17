from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from .repository import EnrolleeResitory
from .service import EnrolleeService


# Enrollee service dependency
def get_enrollee_repository(db: Session = Depends(get_db)) -> EnrolleeResitory:
  return EnrolleeResitory(db)


def get_enrolle_service(
  repository: EnrolleeResitory = Depends(get_enrollee_repository),
) -> EnrolleeService:
  return EnrolleeService(repository)
