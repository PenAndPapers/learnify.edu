from __future__ import annotations

from collections.abc import Callable
from typing import Annotated

from fastapi import Depends

from app.database import DatabaseDep

from .repository import InterviewRepository
from .service import InterviewService
from .table import InterviewSessionTable


def get_interview_repository(db: DatabaseDep) -> InterviewRepository:
  return InterviewRepository(db)


def get_interview_service(
  repository: Annotated[InterviewRepository, Depends(get_interview_repository)],
) -> InterviewService:
  """Build an InterviewService WITHOUT the enrollee-side callback wired in.

  The Enrollee module owns the 'interview → enrollee' feedback callback and
  will construct a patched InterviewService when it needs to orchestrate the
  scheduling or grading side-effects against enrollee rows.
  """

  return InterviewService(repository=repository, on_session_graded=None)


def build_interview_service_with_callback(
  repository: InterviewRepository,
  callback: Callable[[InterviewSessionTable], None] | None,
) -> InterviewService:
  """Factory used by the enrollee module to wire its sync callback."""

  return InterviewService(repository=repository, on_session_graded=callback)


InterviewRepositoryDep = Annotated[
  InterviewRepository, Depends(get_interview_repository)
]
InterviewServiceDep = Annotated[InterviewService, Depends(get_interview_service)]
