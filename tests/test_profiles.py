# tests/test_profiles.py
import shutil
from api.settings import get_settings

def test_list_empty(client):
    # 🔒 تنظيف صارم يمنع تسرّب أي بقايا (مثل 'tamer')
    p = get_settings().profiles_dir
    shutil.rmtree(p, ignore_errors=True)
    p.mkdir(parents=True, exist_ok=True)

    r = client.get("/api/profiles/list")
    assert r.status_code == 200
    assert r.json() == []

def test_save_get_delete_profile(client):
    payload = {
        "name": "uu",
        "profile": {
            "contact": {"email": None},
            "skills": [],
            "languages": [],
            "projects": [],
            "education": [],
            "summary": [],
        },
    }
    r = client.post("/api/profiles/save", json=payload)
    assert r.status_code == 200, r.text

    r = client.get("/api/profiles/get", params={"name": "uu"})
    assert r.status_code == 200
    assert r.json()["name"] == "uu"

    r = client.get("/api/profiles/list")
    assert r.status_code == 200
    assert "uu" in r.json()

    r = client.delete("/api/profiles/delete", params={"name": "uu"})
    assert r.status_code == 200
