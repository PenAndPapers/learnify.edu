from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import ExamRepository
from .service import ExamService
from .table import ExamAttemptTable


def get_exam_repository(db: DatabaseDep) -> ExamRepository:
  return ExamRepository(db)


def get_exam_service(
  repository: Annotated[ExamRepository, Depends(get_exam_repository)],
) -> ExamService:
  """Build an ExamService WITHOUT the enrollee-side callback wired in.

  The Enrollee module owns the 'exam → enrollee' feedback callback and will
  construct a patched ExamService when it needs to orchestrate assignment
  or grading side-effects against enrollee rows. This keeps the dependency
  graph strictly one-directional (enrollee → exam, never exam → enrollee).
  """

  return ExamService(repository=repository, on_attempt_graded=None)


def build_exam_service_with_callback(
  repository: ExamRepository,
  callback: Callable[[ExamAttemptTable], None] | None,
) -> ExamService:
  """Factory used by the enrollee module to wire its sync callback."""

  return ExamService(repository=repository, on_attempt_graded=callback)


ExamRepositoryDep = Annotated[ExamRepository, Depends(get_exam_repository)]
ExamServiceDep = Annotated[ExamService, Depends(get_exam_service)]
