from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/authentication", tags=["Authentication"])


@router.post("/student/create", response_model=None)
async def create_student() -> None:
  pass


@router.get("/student/{id}", response_model=None)
async def get_student() -> None:
  pass


@router.patch("/student/{id}", response_model=None)
async def update_student() -> None:
  pass


@router.delete("/student/{id}", response_model=None)
async def delete_student() -> None:
  pass
