from __future__ import annotations
from fastapi.testclient import TestClient
from api.main import app
import pytest

client = TestClient(app)


@pytest.mark.input
@pytest.mark.view
def test_generate_pdf_normalizes_input_and_returns_pdf(tmp_path):
    """
    Sends a minimally messy payload (skills as a comma string, languages as a string),
    verifies the API normalizes it (via ensure_profile_schema) and returns a valid PDF.
    """
    payload = {
        "theme_name": "aqua-card",
        "ui_lang": "en",
        "rtl_mode": False,
        "profile": {
            # Intentionally 'loose' / messy input to exercise normalization:
            "header": {"name": "Tamer Hamad Faour", "title": "Software Developer"},
            "contact": {"email": "tamer@example.com", "github": "github.com/TamerOnLine"},
            "skills": "FastAPI, PostgreSQL, ReportLab",        # string instead of list
            "languages": "Arabic,English,German",              # string instead of list
            "projects": [
                {"title": "NeuroNexus-AI", "description": "Multi-server AI stack", "url": "https://github.com/..."},
                "FastAPI-Streamlit Template"                   # string (allowed by normalizer)
            ],
        },
        "layout_inline": {
            "flow": [
                # ⚠️ blocks MUST be strings (NOT dicts)
                {"column": "main", "blocks": ["header_name", "key_skills", "projects", "languages"]}
            ]
        },
    }

    res = client.post("/generate-form-simple", json=payload)
    assert res.status_code == 200, res.text

    # content-type check (case-insensitive)
    ctype = res.headers.get("content-type", "")
    assert "application/pdf" in ctype.lower()

    # write and verify size > 2KB
    p = tmp_path / "api_generated.pdf"
    p.write_bytes(res.content)
    assert p.exists() and p.stat().st_size > 2000


@pytest.mark.print
def test_generate_pdf_with_minimal_blocks_returns_pdf(tmp_path):
    """
    Simple 'happy path' with just header + projects to ensure the pipeline works end-to-end.
    """
    payload = {
        "theme_name": "aqua-card",
        "ui_lang": "en",
        "profile": {
            "header": {"name": "Tamer", "title": "Backend & PDF Builder"},
            "contact": {"email": "tamer@example.com"},
            "projects": [
                {"title": "PDF Builder", "description": "ReportLab-based resume generator", "url": "https://example.com"}
            ],
        },
        "layout_inline": {
            "flow": [
                {"column": "main", "blocks": ["header_name", "projects"]}
            ]
        },
    }

    res = client.post("/generate-form-simple", json=payload)
    assert res.status_code == 200, res.text
    assert "application/pdf" in res.headers.get("content-type", "").lower()

    out = tmp_path / "api_print.pdf"
    out.write_bytes(res.content)
    assert out.exists() and out.stat().st_size > 1500
