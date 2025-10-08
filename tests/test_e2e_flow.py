from __future__ import annotations
from pathlib import Path
import pytest
import json

# ----- 1) INPUT -----
@pytest.mark.input
def test_input_schema_minimal():
    # إن وُجدت دالة ensure_profile_schema نستخدمها، وإلا نمرّر كما هو
    try:
        from api.pdf_utils.schema import ensure_profile_schema  # اختياري
    except Exception:
        ensure_profile_schema = lambda x: x  # Fallback

    minimal = {"header": {"name": "Tamer", "title": "Software Dev"}}
    out = ensure_profile_schema(minimal)
    assert "header" in out and "name" in out["header"]

# ----- 2) SAVE (Mock) -----
@pytest.mark.save
def test_save_profile_mock(tmp_path):
    data = {"header": {"name": "Tamer"}}
    f = tmp_path / "profile.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    assert f.exists()

# ----- 3) FETCH (Mock) -----
@pytest.mark.fetch
def test_fetch_profile_mock(tmp_path):
    f = tmp_path / "profile.json"
    f.write_text('{"header":{"name":"Tamer"}}', encoding="utf-8")
    loaded = json.loads(f.read_text(encoding="utf-8"))
    assert loaded["header"]["name"] == "Tamer"

# ----- 4) VIEW (Preview PDF) -----
@pytest.mark.view
def test_preview_pdf_build(tmp_path):
    """
    بناء معاينة PDF خفيفة.
    ملاحظة: يجب أن تكون عناصر blocks عبارة عن أسماء بلوكات (strings).
    """
    from api.pdf_utils.fonts import register_all_fonts
    from api.pdf_utils.builder import build_resume_pdf

    register_all_fonts()

    profile = {
        "header": {"name": "Tamer Hamad Faour", "title": "Software Developer"},
        "contact": {"email": "tamer@example.com"},
    }

    # ⚠️ استخدم أسماء كسلاسل نصية
    layout = {
        "flow": [
            {
                "col": "right",
                "x": 40,
                "y": 780,
                "w": 515,
                "blocks": ["header_name"],  # كان dict سابقاً
            }
        ]
    }

    pdf = build_resume_pdf(
        data={
            "profile": profile,
            "theme_name": "aqua-card",
            "ui_lang": "en",
            "layout_inline": layout,
        }
    )
    out = tmp_path / "preview.pdf"
    out.write_bytes(pdf)
    assert out.exists() and out.stat().st_size > 1000

# ----- 5) PRINT (Final PDF) -----
@pytest.mark.print
def test_print_final_pdf(tmp_path):
    """
    بناء PDF نهائي للطباعة.
    تأكد من أن blocks كلها Strings: ["header_name", "projects", ...]
    """
    from api.pdf_utils.fonts import register_all_fonts
    from api.pdf_utils.builder import build_resume_pdf

    register_all_fonts()

    profile = {
        "header": {"name": "Tamer Hamad Faour", "title": "Software Developer"},
        "contact": {"email": "tamer@example.com", "github": "github.com/TamerOnLine"},
        "skills": ["FastAPI", "PostgreSQL", "ReportLab", "Streamlit"],
        "languages": ["Arabic (Native)", "English", "German"],
        # يمكن إضافة بيانات أخرى لو احتاجتها البلوكات
    }

    # ⚠️ كل العناصر أسماء بلوكات كسلاسل
    layout = {
        "flow": [
            {
                "col": "right",
                "x": 40,
                "y": 780,
                "w": 515,
                "blocks": ["header_name", "projects"],
            },
            {
                "col": "left",
                "x": 20,
                "y": 780,
                "w": 200,
                "blocks": ["contact_info", "key_skills", "languages"],
            },
        ]
    }

    pdf = build_resume_pdf(
        data={
            "profile": profile,
            "theme_name": "aqua-card",
            "ui_lang": "en",
            "layout_inline": layout,
        }
    )
    out = tmp_path / "final_resume.pdf"
    out.write_bytes(pdf)
    assert out.exists() and out.stat().st_size > 2000
