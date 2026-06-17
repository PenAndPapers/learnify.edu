from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["Student"])


@router.get("/student/all", response_model=None)
async def get_students() -> None:
  """Get list of students"""
  pass


@router.post("/student/login", response_model=None)
async def login_student() -> None:
  """Login student"""

  pass


@router.post("/student/create", response_model=None)
async def create_student() -> None:
  """Create student account"""
  pass


@router.get("/student/{uuid}", response_model=None)
async def get_student() -> None:
  """Get student account information"""
  pass


@router.patch("/student/{uuid}", response_model=None)
async def update_student() -> None:
  """Update student account information"""
  pass


@router.delete("/student/{uuid}", response_model=None)
async def delete_student() -> None:
  """Delete student account"""
  pass
