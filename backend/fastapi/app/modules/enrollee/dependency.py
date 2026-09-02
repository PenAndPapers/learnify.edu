from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from ..student.repository import StudentRepository
from .repository import EnrolleeRepository
from .service import EnrolleeService


def get_enrollee_repository(db: DatabaseDep) -> EnrolleeRepository:
  """Get a EnrolleeRepository instance with the database session."""

  return EnrolleeRepository(db)


def get_student_repository(db: DatabaseDep) -> StudentRepository:
  """Get a StudentRepository instance for promotion workflows from the enrollee service."""

  return StudentRepository(db)


def get_enrollee_service(
  enrollee_repository: Annotated[EnrolleeRepository, Depends(get_enrollee_repository)],
  student_repository: Annotated[StudentRepository, Depends(get_student_repository)],
) -> EnrolleeService:
  """Get an EnrolleeService instance with its repositories."""

  return EnrolleeService(
    repository=enrollee_repository, student_repository=student_repository
  )


EnrolleeRepositoryDep = Annotated[EnrolleeRepository, Depends(get_enrollee_repository)]
EnrolleeServiceDep = Annotated[EnrolleeService, Depends(get_enrollee_service)]
