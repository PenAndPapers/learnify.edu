from fastapi import APIRouter

from app.modules.authentication.dependency import TokenServiceDep
from app.modules.authentication.validation import TokenAudience, TokenResponse

from .dependency import EnrolleeServiceDep
from .validation import CreateEnrollee

router = APIRouter(prefix="/api/v1", tags=["Enrollee"])


@router.post("/enrolle/application/register", response_model=TokenResponse)
def student_application_register(
  enrrollee: CreateEnrollee,
  enrolle_service: EnrolleeServiceDep,
  token_service: TokenServiceDep,
) -> TokenResponse:
  new_enrollee = enrolle_service.create(enrrollee)

  if new_enrollee:
    token = token_service.create_auth_tokens(
      TokenAudience(id=new_enrollee.id, uuid=new_enrollee.uuid)
    )

  return token


@router.post("/enrolle/application/verify", response_model=None)
def student_application_verify() -> None:
  pass


@router.post("/enrolle/application/profile", response_model=None)
def student_application_profile() -> None:
  pass


@router.post("/enrolle/application/start", response_model=None)
def student_application_start() -> None:
  pass
