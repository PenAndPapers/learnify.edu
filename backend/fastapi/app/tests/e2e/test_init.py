from fastapi.testclient import TestClient

from app.main import app


def test_e2e_pure_smoke() -> None:
  assert True is not False
  assert list(range(3)) == [0, 1, 2]


def test_e2e_system_index_endpoint() -> None:
  with TestClient(app) as client:
    response = client.get("/api/v1/system/")
    assert response.status_code == 200
    assert response.json() == {"message": "Fastapi web application"}
