def test_list_empty(client):
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
            "summary": "",
        },
    }
    r = client.post("/api/profiles/save", json=payload)
    assert r.status_code == 200, r.text

    r = client.get("/api/profiles/get", params={"name": "uu"})
    assert r.status_code == 200
    assert r.json()["name"] == "uu"

    r = client.get("/api/profiles/list")
    assert "uu" in r.json()

    r = client.delete("/api/profiles/delete", params={"name": "uu"})
    assert r.status_code == 200
