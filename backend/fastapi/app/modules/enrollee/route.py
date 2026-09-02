from typing import Annotated

from fastapi import APIRouter, Body, status
from pydantic import UUID4

from app.modules.exam.validation import ExamAttemptResponse
from app.modules.interview.validation import InterviewSessionResponse
from app.modules.student.validation import StudentResponse

from .dependency import EnrolleeServiceDep
from .validation import (
  AssignEnrolleeExam,
  AssignEnrolleeInterview,
  CreateEnrollee,
  EnrolleeResponse,
  UpdateEnrollee,
  UpdateEnrolleeStatus,
)

router = APIRouter(prefix="/api/v1/enrolle/application", tags=["Enrollee Application"])


@router.post(
  "/",
  status_code=status.HTTP_201_CREATED,
  response_model=EnrolleeResponse,
)
def create(
  enrollee: CreateEnrollee,
  enrolle_service: EnrolleeServiceDep,
):
  new_enrollee = enrolle_service.create(enrollee)
  return EnrolleeResponse.model_validate(new_enrollee)


@router.get("/list", status_code=status.HTTP_200_OK, response_model=EnrolleeResponse)
def list_of_enrollees():
  pass


@router.get("/{uuid}", status_code=status.HTTP_200_OK, response_model=EnrolleeResponse)
def read(uuid: UUID4, enrolle_service: EnrolleeServiceDep):
  enrollee = enrolle_service.get_enrollee(str(uuid))
  return EnrolleeResponse.model_validate(enrollee)


@router.patch(
  "/{uuid}", status_code=status.HTTP_200_OK, response_model=EnrolleeResponse
)
def update(
  uuid: UUID4,
  payload: Annotated[UpdateEnrollee, Body()],
  enrolle_service: EnrolleeServiceDep,
):
  enrollee = enrolle_service.update_enrollee(str(uuid), payload)
  return EnrolleeResponse.model_validate(enrollee)


@router.patch(
  "/{uuid}/status",
  status_code=status.HTTP_200_OK,
  response_model=EnrolleeResponse,
)
def update_status(
  uuid: UUID4,
  payload: UpdateEnrolleeStatus,
  enrolle_service: EnrolleeServiceDep,
):
  enrollee = enrolle_service.update_enrollee_status(str(uuid), payload)
  return EnrolleeResponse.model_validate(enrollee)


@router.patch(
  "/{uuid}/promote",
  status_code=status.HTTP_201_CREATED,
  response_model=StudentResponse,
)
def promote(
  uuid: UUID4,
  enrolle_service: EnrolleeServiceDep,
  payload: Annotated[UpdateEnrolleeStatus | None, Body()] = None,
):
  by_employee_id = payload.by_employee_id if payload is not None else None
  student = enrolle_service.promote_to_student(str(uuid), by_employee_id)
  return StudentResponse.model_validate(student)


@router.patch(
  "/update/status/{uuid}",
  status_code=status.HTTP_200_OK,
  response_model=EnrolleeResponse,
  deprecated=True,
)
def update_status_legacy(
  uuid: UUID4,
  status_payload: UpdateEnrolleeStatus,
  enrolle_service: EnrolleeServiceDep,
):
  enrollee = enrolle_service.update_enrollee_status(str(uuid), status_payload)
  return EnrolleeResponse.model_validate(enrollee)


@router.post(
  "/{uuid}/assign-exam",
  status_code=status.HTTP_201_CREATED,
  response_model=ExamAttemptResponse,
)
def assign_exam(
  uuid: UUID4,
  payload: AssignEnrolleeExam,
  enrolle_service: EnrolleeServiceDep,
):
  """Assign an entrance exam to this enrollee.

  Creates an ExamAttempt row, generates the shared exam-link UUID,
  writes the link + pass-score snapshot back onto the enrollee, and
  transitions application_status → EXAM_PENDING.
  """

  attempt = enrolle_service.assign_exam(str(uuid), payload)
  return ExamAttemptResponse.model_validate(attempt)


@router.get(
  "/exam/{exam_uuid}",
  status_code=status.HTTP_200_OK,
  response_model=EnrolleeResponse,
)
def get_by_exam_uuid(
  exam_uuid: UUID4,
  enrolle_service: EnrolleeServiceDep,
):
  """Lookup an enrollee by the shared exam-link UUID stored on their row."""

  enrollee = enrolle_service.get_enrollee_by_exam_link(str(exam_uuid))
  return EnrolleeResponse.model_validate(enrollee)


@router.post(
  "/{uuid}/schedule-interview",
  status_code=status.HTTP_201_CREATED,
  response_model=InterviewSessionResponse,
)
def schedule_interview(
  uuid: UUID4,
  payload: AssignEnrolleeInterview,
  enrolle_service: EnrolleeServiceDep,
):
  """Schedule an interview for this enrollee.

  Creates an InterviewSession row, generates the shared session-link UUID,
  writes the link + pass-score snapshot back onto the enrollee, marks
  interview_required=True, and transitions application_status → INTERVIEW_PENDING.
  """

  session = enrolle_service.schedule_interview(str(uuid), payload)
  return InterviewSessionResponse.model_validate(session)


@router.get(
  "/interview/{interview_uuid}",
  status_code=status.HTTP_200_OK,
  response_model=EnrolleeResponse,
)
def get_by_interview_uuid(
  interview_uuid: UUID4,
  enrolle_service: EnrolleeServiceDep,
):
  """Lookup an enrollee by the shared interview session-link UUID stored on their row."""

  enrollee = enrolle_service.get_enrollee_by_interview_link(str(interview_uuid))
  return EnrolleeResponse.model_validate(enrollee)
