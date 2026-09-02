from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep
from app.modules.exam.dependency import build_exam_service_with_callback
from app.modules.exam.repository import ExamRepository

from ..student.repository import StudentRepository
from .repository import EnrolleeRepository
from .service import EnrolleeService
from .table import EnrolleeTable


def get_enrollee_repository(db: DatabaseDep) -> EnrolleeRepository:
  """Get a EnrolleeRepository instance with the database session."""

  return EnrolleeRepository(db)


def get_student_repository(db: DatabaseDep) -> StudentRepository:
  """Get a StudentRepository instance for promotion workflows from the enrollee service."""

  return StudentRepository(db)


def get_exam_repository(db: DatabaseDep) -> ExamRepository:
  """ExamRepository for assignment + grading orchestration."""

  return ExamRepository(db)


def _make_exam_service_factory(
  exam_repository: ExamRepository,
) -> Callable:
  """Return a closure that ExamService on-demand with a caller-provided callback.

  The enrollee service calls this with its on_attempt_graded callback so that
  whenever the exam service grades a submission, the enrollee's exam_status,
  score, and application_status columns are kept in sync — all within the
  same transaction (same db session).
  """

  def factory(callback):
    return build_exam_service_with_callback(exam_repository, callback)

  return factory


def get_enrollee_service(
  enrollee_repository: Annotated[EnrolleeRepository, Depends(get_enrollee_repository)],
  student_repository: Annotated[StudentRepository, Depends(get_student_repository)],
  exam_repository: Annotated[ExamRepository, Depends(get_exam_repository)],
) -> EnrolleeService:
  """Get an EnrolleeService instance with its repositories + exam orchestration."""

  return EnrolleeService(
    repository=enrollee_repository,
    student_repository=student_repository,
    exam_service_factory=_make_exam_service_factory(exam_repository),
  )


EnrolleeRepositoryDep = Annotated[EnrolleeRepository, Depends(get_enrollee_repository)]
EnrolleeServiceDep = Annotated[EnrolleeService, Depends(get_enrollee_service)]
__all__ = [
  "EnrolleeRepositoryDep",
  "EnrolleeServiceDep",
  "get_enrollee_service",
  "get_enrollee_repository",
  "EnrolleeTable",
]
