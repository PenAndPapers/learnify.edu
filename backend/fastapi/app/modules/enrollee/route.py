from fastapi import APIRouter

from app.modules.authentication.dependency import TokenServiceDep
from app.modules.authentication.validation import TokenAudience, TokenResponse

from .dependency import EnrolleeServiceDep
from .validation import CreateEnrollee

router = APIRouter(prefix="/api/v1/enrolle/application", tags=["Enrollee"])


@router.get("/", response_model=None)
def get_enrollees() -> None:
  """Get all enrollee application list"""
  pass


@router.post("/", response_model=TokenResponse)
def enrollee_application_register(
  enrrollee: CreateEnrollee,
  enrolle_service: EnrolleeServiceDep,
  token_service: TokenServiceDep,
) -> TokenResponse:
  """Enrollee application register. Enrollee can register their application and get the access token.
  The access token will be used to access the enrollee application profile and take the examination for the application.
  """

  new_enrollee = enrolle_service.create(enrrollee)

  if new_enrollee:
    audience = {"id": new_enrollee.id, "uuid": new_enrollee.uuid}
    token = token_service.create_auth_tokens(TokenAudience(**audience))

  return token


@router.post("/activate/{uuid}", response_model=None)
def enrollee_activate_account(token_code: str) -> None:
  """Enrollee activate their account by clicking the activation link sent to their email."""
  pass


@router.get("/{uuid}", response_model=None)
def enrollee_application_profile() -> None:
  """Get enrollee application profile. Enrollee can view their application profile and status if application is approved, rejected, or pending."""
  pass


@router.patch("/verify/{uuid}", response_model=None)
def enrollee_application_update() -> None:
  """School admin can approve or reject the enrollee application.
  If the application is approved, the enrollee can take the examination for the application.
  """
  pass


@router.get("/exam/questions/", response_model=None)
def enrollee_examination_questions() -> None:
  """Get enrollee examination questions. Enrollee can view the examination questions for the application.
  Only enrollee with active account and verified application can view the examination questions.
  """
  pass


@router.post("/exam/{uuid}", response_model=None)
def enrollee_examination() -> None:
  """Enrollee examination. Enrollee can take the examination for the application.
  Only enrollee with active account and verified application can take the examination.

  Calculates the score of the examination and return the result to the enrollee.
  """
  pass


@router.get("/exam/result/{uuid}", response_model=None)
def enrollee_examination_result() -> None:
  """Get enrollee examination result. Enrollee can view their examination result after taking the examination."""
  pass
