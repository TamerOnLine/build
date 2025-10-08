import os
from pathlib import Path
import pytest

# بلوكات قد تعتمد على أصول/صور أو زخارف — نتخطّاها في اختبار الـsmoke
SKIP_BLOCKS = {
    "avatar_circle",
    "left_panel_bg",
    "decor_curve",
    "header_bar",
}

@pytest.mark.view
def test_block_smoke():
    """
    يبني PDF بسيط يحتوي بلوك واحد فقط.
    ملاحظة مهمة: عناصر blocks يجب أن تكون سلاسل نصية (أسماء البلوكات)،
    لأن builder.py يتوقع strings (مثل "header_name" أو "header_name:arg").
    """
    block_id = os.getenv("BLOCK_ID", "header_name")

    if block_id in SKIP_BLOCKS:
        pytest.skip(f"Skipping decorative/asset-dependent block: {block_id}")

    from api.pdf_utils.fonts import register_all_fonts
    from api.pdf_utils.builder import build_resume_pdf

    register_all_fonts()

    # ⚠️ استخدم أسماء البلوكات كسلاسل نصية
    layout = {
        "flow": [
            {"col": "right", "x": 40, "y": 780, "w": 515, "blocks": [block_id]}
        ]
    }

    profile = {
        "header": {"name": "Tamer OnLine", "title": "Software Developer"},
        "contact": {"email": "me@example.com"},
    }

    payload = {
        "profile": profile,
        "theme_name": "aqua-card",
        "ui_lang": "en",
        "rtl_mode": False,
        "layout_inline": layout,
    }

    pdf = build_resume_pdf(data=payload)
    out = Path("out"); out.mkdir(exist_ok=True)
    p = out / f"smoke_{block_id}.pdf"
    p.write_bytes(pdf)
    assert p.exists() and p.stat().st_size > 1000, "PDF too small or not written"
