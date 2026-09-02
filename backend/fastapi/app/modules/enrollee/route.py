from typing import Annotated

from fastapi import APIRouter, Body, status
from pydantic import UUID4

from app.modules.student.validation import StudentResponse

from .dependency import EnrolleeServiceDep
from .validation import (
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


@router.get(
  "/exam/{exam_uuid}",
  status_code=status.HTTP_200_OK,
  response_model=EnrolleeResponse,
)
def get_by_exam_uuid(
  exam_uuid: UUID4,
  enrolle_service: EnrolleeServiceDep,
):
  """Lookup an enrollee by their exam link UUID (placeholder until the exam module is built)."""

  _ = exam_uuid
  _ = enrolle_service
  pass
