from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.main import app


# Define a fixture that automatically handles application startup and shutdown
@pytest.fixture(scope="module")
def client():
  # The 'with' statement triggers FastAPI's startup/lifespan events
  with TestClient(app) as test_client:
    yield test_client
  # Code after yield runs during test teardown (shutdown events)


def test_index(client):
  response = client.get("/")
  assert response.status_code == 200
  assert response.json() == {"message": "Fastapi web application"}


def test_db_connection(client):
  response = client.get("/check-database")
  assert response.status_code == 200
  assert response.json() == {"message": "Database connection successful"}


def test_redis_connection(client, mocker):
  # Mock .incr() since endpoint calls it first
  mocker.patch("app.main.app.state.redis.incr", new_callable=AsyncMock)

  # Redis naturally returns string values as bytes (e.g., b"1")
  # Mock .get() as an AsyncMock that returns the expected bytes object
  mock_get = mocker.patch(
    "app.main.app.state.redis.get",
    new_callable=AsyncMock,
    return_value=b"1",
  )

  response = client.get("/check-redis")

  assert response.status_code == 200
  assert response.json() == {"hits": "1"}

  mock_get.assert_called_once_with("hits")


def test_health_check(client):
  response = client.get("/check-health")
  assert response.status_code == 200
  assert response.json() == {"status": "healthy"}
