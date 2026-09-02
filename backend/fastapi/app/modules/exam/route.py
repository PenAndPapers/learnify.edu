from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, status
from pydantic import UUID4

from .dependency import ExamServiceDep
from .validation import (
  AssignExamRequest,
  CreateExam,
  ExamAttemptResponse,
  ExamListItemResponse,
  ExamResponse,
  GradedExamAttemptResponse,
  SubmitExamAttempt,
  UpdateExam,
)

router = APIRouter(prefix="/api/v1/exams", tags=["Exams"])


# ---------- Exam template CRUD ----------


@router.post(
  "/",
  status_code=status.HTTP_201_CREATED,
  response_model=ExamResponse,
)
def create_exam(
  payload: CreateExam,
  exam_service: ExamServiceDep,
):
  exam = exam_service.create_exam(payload)
  return ExamResponse.model_validate(exam)


@router.get(
  "/",
  status_code=status.HTTP_200_OK,
  response_model=list[ExamListItemResponse],
)
def list_active_exams(exam_service: ExamServiceDep):
  exams = exam_service.list_active_exams()
  return [exam_service.to_list_item(ex) for ex in exams]


@router.get(
  "/{uuid}",
  status_code=status.HTTP_200_OK,
  response_model=ExamResponse,
)
def get_exam(
  uuid: UUID4,
  exam_service: ExamServiceDep,
):
  exam = exam_service.get_exam(str(uuid))
  return ExamResponse.model_validate(exam)


@router.patch(
  "/{uuid}",
  status_code=status.HTTP_200_OK,
  response_model=ExamResponse,
)
def update_exam(
  uuid: UUID4,
  payload: Annotated[UpdateExam, Body()],
  exam_service: ExamServiceDep,
):
  exam = exam_service.update_exam(str(uuid), payload)
  return ExamResponse.model_validate(exam)


@router.delete(
  "/{uuid}",
  status_code=status.HTTP_204_NO_CONTENT,
)
def archive_exam(
  uuid: UUID4,
  exam_service: ExamServiceDep,
):
  from fastapi import Response

  exam_service.archive_exam(str(uuid))
  return Response(status_code=status.HTTP_204_NO_CONTENT)


# ---------- Assignment (placeholder — enrollee module owns the full flow) ----------


@router.post(
  "/assign",
  status_code=status.HTTP_201_CREATED,
  response_model=ExamAttemptResponse,
  deprecated=True,
)
def assign_exam(
  payload: AssignExamRequest,
  exam_service: ExamServiceDep,
):
  """Low-level assign endpoint. Prefer the enrollee-specific assignment
  endpoint in the enrollee module, which syncs application status + audit
  fields atomically."""

  _ = payload
  _ = exam_service
  from .exception import ExamAttemptNotFoundException

  raise ExamAttemptNotFoundException(
    "Use /api/v1/enrolle/application/{uuid}/assign-exam instead."
  )


# ---------- Public attempt lifecycle ----------


@router.get(
  "/link/{attempt_uuid}",
  status_code=status.HTTP_200_OK,
  response_model=ExamResponse,
)
def get_exam_by_attempt_link(
  attempt_uuid: UUID4,
  exam_service: ExamServiceDep,
):
  """Fetch exam questions via the shared attempt UUID.

  Expiry / enrollee ownership is enforced in the enrollee-specific route;
  this endpoint simply looks up the exam template behind the attempt.
  """

  attempt = exam_service.get_attempt(str(attempt_uuid))
  exam = exam_service.repository.get_by_id(attempt.exam_id)
  return ExamResponse.model_validate(exam)


@router.get(
  "/attempt/{attempt_uuid}",
  status_code=status.HTTP_200_OK,
  response_model=ExamAttemptResponse,
)
def get_attempt(
  attempt_uuid: UUID4,
  exam_service: ExamServiceDep,
):
  attempt = exam_service.get_attempt(str(attempt_uuid))
  return ExamAttemptResponse.model_validate(attempt)


@router.post(
  "/attempt/{attempt_uuid}/start",
  status_code=status.HTTP_200_OK,
  response_model=ExamAttemptResponse,
)
def start_attempt(
  attempt_uuid: UUID4,
  exam_service: ExamServiceDep,
):
  attempt = exam_service.start_attempt(str(attempt_uuid))
  return ExamAttemptResponse.model_validate(attempt)


@router.post(
  "/attempt/{attempt_uuid}/submit",
  status_code=status.HTTP_200_OK,
  response_model=GradedExamAttemptResponse,
)
def submit_attempt(
  attempt_uuid: UUID4,
  payload: SubmitExamAttempt,
  exam_service: ExamServiceDep,
):
  attempt = exam_service.submit_attempt(str(attempt_uuid), payload)
  return exam_service.to_graded_response(attempt)


@router.get(
  "/attempt/{attempt_uuid}/result",
  status_code=status.HTTP_200_OK,
  response_model=GradedExamAttemptResponse,
)
def get_attempt_result(
  attempt_uuid: UUID4,
  exam_service: ExamServiceDep,
):
  attempt = exam_service.get_attempt(str(attempt_uuid))
  return exam_service.to_graded_response(attempt)
