from fastapi import APIRouter, Depends

from app.modules.user.dependency import get_enrolle_service
from app.modules.user.service import EnrolleeService
from app.modules.user.validation import CreateEnrollee

from .dependency import get_token_service
from .service import TokenService
from .validation import TokenAudience, TokenResponse

router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.post("/enrolle/application/register", response_model=TokenResponse)
async def student_application_register(
  enrrollee: CreateEnrollee,
  enrolle_service: EnrolleeService = Depends(get_enrolle_service),
  token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
  enrollee = enrolle_service.create(enrrollee)

  if enrollee:
    token = token_service.create_auth_tokens(
      TokenAudience(id=enrollee.id, uuid=enrollee.uuid, user_type=enrollee.user_type)
    )

  return token


@router.post("/enrolle/application/verify", response_model=None)
async def student_application_verify() -> None:
  pass


@router.post("/enrolle/application/profile", response_model=None)
async def student_application_profile() -> None:
  pass


@router.post("/enrolle/application/start", response_model=None)
async def student_application_start() -> None:
  pass
