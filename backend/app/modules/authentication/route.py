from fastapi import APIRouter

router = APIRouter(prefix='/api/v1/authentication', tags=['Authentication'])


@router.post('/student/application/register', response_model=None)
def student_application_register() -> None:
    pass


@router.post('/student/application/verify', response_model=None)
def student_application_verify() -> None:
    pass


@router.post('/student/application/profile', response_model=None)
def student_application_profile() -> None:
    pass


@router.post('/student/application/start', response_model=None)
def student_application_start() -> None:
    pass
