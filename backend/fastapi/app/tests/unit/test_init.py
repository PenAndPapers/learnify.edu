def test_unit_smoke_pure_python() -> None:
  assert 1 + 1 == 2
  assert isinstance("learnify", str)


def test_app_package_importable() -> None:
  import app

  assert hasattr(app, "main")
  assert hasattr(app, "route")
