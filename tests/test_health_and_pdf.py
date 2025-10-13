def test_healthz(client):
    r = client.get("/healthz")
    assert r.status_code == 200
    js = r.json()
    assert isinstance(js, dict)
    assert js.get("ok") in (True, "healthy", None)


def test_generate_form_simple_minimal(client):
    payload = {
        "profile": {
            "contact": {"email": None},
            "skills": ["Python"],
            "languages": ["EN"],
            "projects": [["Title", "Desc", "https://example.com"]],
            "education": [["BSc", "Uni", "2020", "2024", "", ""]],
            # ✅ قائمة وليس سلسلة
            "summary": [],
        },
        "ui_lang": "en",
        "rtl_mode": False,
        "theme_name": "default",
        # flow/columns يمكن أن يولَّد افتراضيًا، لذلك نرسل بنية خفيفة
        "layout_inline": {"flow": [{"column": "main", "blocks": ["header_name"]}]},
    }
    r = client.post("/generate-form-simple", json=payload)
    assert r.status_code in (200, 201)
    # تَوقّع PDF
    ctype = (r.headers.get("content-type") or "").lower()
    assert "application/pdf" in ctype
    assert len(r.content) > 1000
