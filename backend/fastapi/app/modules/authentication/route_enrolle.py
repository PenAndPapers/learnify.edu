from fastapi import APIRouter, Depends

from app.modules.user.dependency import get_enrolle_service, get_user_service
from app.modules.user.service import EnrolleeService, UserService
from app.modules.user.validation import CreateEnrollee

from .dependency import get_token_service
from .service import TokenService
from .validation import TokenAudience, TokenResponse, TokenRefreshRequest, TokenValidateRequest


router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(
  token: TokenRefreshRequest,
  token_service: TokenService = Depends(get_token_service),
  user_service: UserService = Depends(get_user_service)
) -> TokenResponse:
  token = token_service.refresh_token(token, user_service)
  
  return token


@router.post("/token/validate", response_model=bool)
async def validate_token(token: TokenValidateRequest, token_service: TokenService = Depends(get_token_service)) -> bool:
  token = token_service.validate_token(token)
  
  return token is not None


@router.post("/enrolle/application/register", response_model=TokenResponse)
async def student_application_register(
  enrrollee: CreateEnrollee,
  enrolle_service: EnrolleeService = Depends(get_enrolle_service),
  token_service: TokenService = Depends(get_token_service),
) -> TokenResponse:
  enrollee = enrolle_service.create(enrrollee)

  if enrollee:
    token = token_service.create_auth_tokens(
      TokenAudience(id=enrollee.id, uuid=enrollee.uuid)
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
