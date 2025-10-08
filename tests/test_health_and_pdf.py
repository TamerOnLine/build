def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    assert isinstance(r.json(), dict)

def test_generate_form_simple_minimal(client):
    payload = {
        "profile": {
            "contact": {"email": None},
            "skills": ["Python"],
            "languages": ["EN"],
            "projects": [["Title", "Desc", "https://example.com"]],
            "education": [["BSc", "Uni", "2020", "2024", "", ""]],
            "summary": "Hello",
        },
        "ui_lang": "en",
        "rtl_mode": False,
        "theme_name": "default",
        "layout_inline": {"blocks": []},
    }
    r = client.post("/generate-form-simple", json=payload)
    assert r.status_code in (200, 201)
