import os
import shutil
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(autouse=True)
def _tmp_profiles_dir(tmp_path, monkeypatch):
    d = tmp_path / "profiles"
    d.mkdir()
    monkeypatch.setenv("PROFILES_DIR", str(d))
    yield
    os.environ.pop("PROFILES_DIR", None)
    shutil.rmtree(tmp_path, ignore_errors=True)

# ✅ خليها function-scoped وتعتمد على _tmp_profiles_dir
@pytest.fixture()
def app(_tmp_profiles_dir):
    from api.main import app as _app
    return _app

@pytest.fixture()
def client(app):
    return TestClient(app)
