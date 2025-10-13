# tests/conftest.py
from __future__ import annotations
import importlib
import shutil
import pytest

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    يعزل كل اختبار في مجلد profiles مؤقت عبر PROFILES_DIR،
    يفرّغ كاش get_settings، ثم يعيد تحميل الوحدات بالترتيب الصحيح.
    """
    # 0) أنشئ مجلد profiles معزول داخل tmp_path
    profiles_root = tmp_path / "profiles_isolated"
    profiles_root.mkdir(parents=True, exist_ok=True)

    # 1) وجّه التطبيق لاستخدامه
    monkeypatch.setenv("PROFILES_DIR", str(profiles_root))
    monkeypatch.setenv("PUBLIC_PROFILES_MOUNT", "/profiles")

    # 2) أعد تحميل settings وافرغ كاش get_settings لو مزوّد بـ lru_cache
    from api import settings as settings_mod
    importlib.reload(settings_mod)
    get_settings = getattr(settings_mod, "get_settings", None)
    cache_clear = getattr(get_settings, "cache_clear", None)
    if callable(cache_clear):
        cache_clear()

    # 3) أعد تحميل الراوتر الذي يمسك PROFILES_DIR عند الاستيراد
    from api.routes import profiles as profiles_mod
    importlib.reload(profiles_mod)

    # 4) أعد تحميل main ليبني app على الإعدادات المعزولة
    from api import main as main_mod
    importlib.reload(main_mod)

    from starlette.testclient import TestClient
    return TestClient(main_mod.app)
