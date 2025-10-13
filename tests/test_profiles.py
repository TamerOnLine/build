def test_list_empty(client):
    r = client.get("/api/profiles/list")
    assert r.status_code == 200
    # لا توجد بروفايلات محفوظة (لا مجلدات باسم البروفايل تحتوي profile.json)
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
            # ✅ المشروع يعتمد summary كقائمة نصوص
            "summary": [],
        },
    }
    # حفظ
    r = client.post("/api/profiles/save", json=payload)
    assert r.status_code == 200, r.text

    # جلب
    r = client.get("/api/profiles/get", params={"name": "uu"})
    assert r.status_code == 200
    data = r.json()
    assert data["name"] == "uu"
    assert isinstance(data["profile"], dict)

    # يظهر في القائمة لأنه profiles/uu/profile.json موجود
    r = client.get("/api/profiles/list")
    assert r.status_code == 200
    assert "uu" in r.json()

    # حذف
    r = client.delete("/api/profiles/delete", params={"name": "uu"})
    assert r.status_code == 200

    # بعد الحذف يختفي من القائمة
    r = client.get("/api/profiles/list")
    assert r.status_code == 200
    assert "uu" not in r.json()
