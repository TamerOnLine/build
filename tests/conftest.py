# tests/conftest.py
from __future__ import annotations
import importlib
import pytest

@pytest.fixture
def client(tmp_path, monkeypatch):
    """
    يعزل كل اختبار في مجلد profiles مؤقت خاص به عبر PROFILES_DIR،
    ثم يُعيد تحميل الوحدات بالترتيب الصحيح حتى تلتقط القيم الجديدة.
    """
    # مجلد profiles معزول لهذا الاختبار
    profiles_root = tmp_path / "profiles_isolated"
    profiles_root.mkdir(parents=True, exist_ok=True)

    # وجّه التطبيق لاستخدامه
    monkeypatch.setenv("PROFILES_DIR", str(profiles_root))
    monkeypatch.setenv("PUBLIC_PROFILES_MOUNT", "/profiles")

    # 1) أعد تحميل settings لقراءة env الجديدة
    from api import settings as settings_mod
    importlib.reload(settings_mod)

    # 2) أعد تحميل الراوتر الذي يخبّئ PROFILES_DIR عند الاستيراد
    from api.routes import profiles as profiles_mod
    importlib.reload(profiles_mod)

    # 3) أخيرًا أعد تحميل main ليبني app بالوضع المعزول
    from api import main as main_mod
    importlib.reload(main_mod)

    from starlette.testclient import TestClient
    return TestClient(main_mod.app)
