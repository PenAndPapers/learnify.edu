from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import StudentResitory
from .service import StudentService


# Student service dependency
def get_student_repository(db: DatabaseDep) -> StudentResitory:
  return StudentResitory(db)


StudentRepositoryDep = Annotated[StudentResitory, Depends(get_student_repository)]


def get_student_service(
  repository: StudentRepositoryDep,
) -> StudentService:
  return StudentService(repository)


StudentServiceDep = Annotated[StudentService, Depends(get_student_service)]
