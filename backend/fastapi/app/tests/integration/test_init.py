def test_integration_pure_smoke() -> None:
  assert 2 * 3 == 6
  assert sorted([3, 1, 2]) == [1, 2, 3]


def test_integration_database_engine_configured() -> None:
  from sqlalchemy.engine import Engine as _Engine

  from app.database import engine

  assert isinstance(engine, _Engine)
  assert hasattr(engine, "url")
  assert str(engine.url.drivername).startswith("postgresql")
