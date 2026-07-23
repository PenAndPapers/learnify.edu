from fastapi import APIRouter, Response, status

from .dependency import StudentServiceDep
from .validation import CreateStudent, StudentResponse

router = APIRouter(prefix="/api/v1/student", tags=["Student"])


@router.get("/", response_model=None)
def get_students() -> None:
  """Get all student list"""
  pass


@router.post("/login", response_model=None)
def login_student() -> None:
  """Login a student account"""
  pass


@router.post("/", response_model=StudentResponse)
def create_student(
  student: CreateStudent, student_service: StudentServiceDep
) -> StudentResponse:
  """Create a student account"""
  new_student = student_service.create(student)

  return new_student


@router.get("/{uuid}", response_model=StudentResponse)
def get_student(uuid: str, student_service: StudentServiceDep) -> StudentResponse:
  """Get student account information"""

  student = student_service.read(uuid)

  return StudentResponse.model_validate(student)


@router.patch("/{uuid}", response_model=None)
def update_student() -> None:
  """Update student account information"""
  pass


@router.delete("/{uuid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(uuid: str, student_service: StudentServiceDep) -> Response:
  """Delete student account"""

  student_service.delete(uuid)

  return Response(status_code=status.HTTP_204_NO_CONTENT)
