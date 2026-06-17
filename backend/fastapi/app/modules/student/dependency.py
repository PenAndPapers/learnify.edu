from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db

from .repository import StudentResitory
from .service import StudentService


# Student service dependency
def get_student_repository(db: Session = Depends(get_db)) -> StudentResitory:
  return StudentResitory(db)


def get_student_service(
  repository: StudentResitory = Depends(get_student_repository),
) -> StudentService:
  return StudentService(repository)
