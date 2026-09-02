from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Response, status
from pydantic import UUID4

from .dependency import InterviewServiceDep
from .validation import (
  CreateInterview,
  GradedInterviewSessionResponse,
  GradeInterviewSession,
  InterviewListItemResponse,
  InterviewResponse,
  InterviewSessionResponse,
  ScheduleInterviewRequest,
  SubmitInterviewSession,
  UpdateInterview,
)

router = APIRouter(prefix="/api/v1/interviews", tags=["Interviews"])


# ---------- Interview template CRUD ----------


@router.post(
  "/",
  status_code=status.HTTP_201_CREATED,
  response_model=InterviewResponse,
)
def create_interview(
  payload: CreateInterview,
  interview_service: InterviewServiceDep,
):
  interview = interview_service.create_interview(payload)
  return InterviewResponse.model_validate(interview)


@router.get(
  "/",
  status_code=status.HTTP_200_OK,
  response_model=list[InterviewListItemResponse],
)
def list_active_interviews(interview_service: InterviewServiceDep):
  interviews = interview_service.list_active_interviews()
  return [interview_service.to_list_item(it) for it in interviews]


@router.get(
  "/{uuid}",
  status_code=status.HTTP_200_OK,
  response_model=InterviewResponse,
)
def get_interview(
  uuid: UUID4,
  interview_service: InterviewServiceDep,
):
  interview = interview_service.get_interview(str(uuid))
  return InterviewResponse.model_validate(interview)


@router.patch(
  "/{uuid}",
  status_code=status.HTTP_200_OK,
  response_model=InterviewResponse,
)
def update_interview(
  uuid: UUID4,
  payload: Annotated[UpdateInterview, Body()],
  interview_service: InterviewServiceDep,
):
  interview = interview_service.update_interview(str(uuid), payload)
  return InterviewResponse.model_validate(interview)


@router.delete(
  "/{uuid}",
  status_code=status.HTTP_204_NO_CONTENT,
)
def archive_interview(
  uuid: UUID4,
  interview_service: InterviewServiceDep,
):
  interview_service.archive_interview(str(uuid))
  return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- Session scheduling (placeholder — enrollee module owns the full flow) ----------


@router.post(
  "/schedule",
  status_code=status.HTTP_201_CREATED,
  response_model=InterviewSessionResponse,
  deprecated=True,
)
def schedule_interview(
  payload: ScheduleInterviewRequest,
  interview_service: InterviewServiceDep,
):
  """Low-level schedule endpoint. Prefer the enrollee-specific scheduling
  endpoint in the enrollee module, which syncs application status + audit
  fields atomically."""

  _ = payload
  _ = interview_service
  from .exception import InterviewSessionNotFoundException

  raise InterviewSessionNotFoundException(
    "Use /api/v1/enrolle/application/{uuid}/schedule-interview instead."
  )


# ---------- Public session lifecycle ----------


@router.get(
  "/link/{session_uuid}",
  status_code=status.HTTP_200_OK,
  response_model=InterviewResponse,
)
def get_interview_by_session_link(
  session_uuid: UUID4,
  interview_service: InterviewServiceDep,
):
  """Fetch interview questions via the shared session UUID.

  Expiry / enrollee ownership is enforced in the enrollee-specific route;
  this endpoint simply looks up the interview template behind the session.
  """

  session = interview_service.get_session(str(session_uuid))
  interview = interview_service.repository.get_by_id(session.interview_id)
  return InterviewResponse.model_validate(interview)


@router.get(
  "/session/{session_uuid}",
  status_code=status.HTTP_200_OK,
  response_model=InterviewSessionResponse,
)
def get_session(
  session_uuid: UUID4,
  interview_service: InterviewServiceDep,
):
  session = interview_service.get_session(str(session_uuid))
  return InterviewSessionResponse.model_validate(session)


@router.post(
  "/session/{session_uuid}/start",
  status_code=status.HTTP_200_OK,
  response_model=InterviewSessionResponse,
)
def start_session(
  session_uuid: UUID4,
  interview_service: InterviewServiceDep,
):
  session = interview_service.start_session(str(session_uuid))
  return InterviewSessionResponse.model_validate(session)


@router.post(
  "/session/{session_uuid}/submit",
  status_code=status.HTTP_200_OK,
  response_model=InterviewSessionResponse,
)
def submit_session(
  session_uuid: UUID4,
  payload: SubmitInterviewSession,
  interview_service: InterviewServiceDep,
):
  """Submit (complete) an interview session. This auto-grades MCQ and RATING
  items but SHORT_ANSWER items remain ungraded until a rater calls /grade."""

  session = interview_service.submit_session(str(session_uuid), payload)
  return InterviewSessionResponse.model_validate(session)


@router.post(
  "/session/{session_uuid}/grade",
  status_code=status.HTTP_200_OK,
  response_model=GradedInterviewSessionResponse,
)
def grade_session(
  session_uuid: UUID4,
  payload: GradeInterviewSession,
  interview_service: InterviewServiceDep,
):
  """Manually grade (or re-grade) a submitted interview session.

  Sets SHORT_ANSWER correctness/points via answer_grades and optionally
  overrides the overall score. Fires the enrollee-side sync callback if
  the enrollee orchestrator wired one in.
  """

  session = interview_service.grade_session(str(session_uuid), payload)
  return interview_service.to_graded_response(session)


@router.delete(
  "/session/{session_uuid}",
  status_code=status.HTTP_204_NO_CONTENT,
)
def cancel_session(
  session_uuid: UUID4,
  interview_service: InterviewServiceDep,
):
  interview_service.cancel_session(str(session_uuid))
  return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
  "/session/{session_uuid}/result",
  status_code=status.HTTP_200_OK,
  response_model=GradedInterviewSessionResponse,
)
def get_session_result(
  session_uuid: UUID4,
  interview_service: InterviewServiceDep,
):
  session = interview_service.get_session(str(session_uuid))
  return interview_service.to_graded_response(session)
