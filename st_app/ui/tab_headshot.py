# st_app/ui/tab_headshot.py
from __future__ import annotations
import base64
import io
from pathlib import Path

import streamlit as st
from PIL import Image


def _resolve_image_source(src: str | None) -> str | None:
    """
    يحوّل المسار/الرابط المُدخل إلى مصدر مفهوم لـ st.image:
    - data:image/... (Base64) -> كما هي
    - http(s)://         -> كما هو
    - /profiles/...      -> يسبقها api_origin من الجلسة
    - مسار ملف محلي      -> إن وُجد، يُعاد كما هو
    وإلا -> None
    """
    if not src:
        return None
    s = str(src).strip()
    if not s:
        return None

    # base64 data url
    if s.startswith("data:image"):
        return s

    # http(s) full URL
    if s.lower().startswith("http://") or s.lower().startswith("https://"):
        return s

    # absolute path served by FastAPI static mount (e.g. /profiles/...)
    if s.startswith("/"):
        origin = st.session_state.get("api_origin", "")
        return (origin + s) if origin else s

    # local file path
    p = Path(s)
    if p.exists() and p.is_file():
        return s

    return None


def render_headshot_tab():
    st.subheader("Headshot / Avatar")

    col1, col2 = st.columns([2, 1])

    # إدخال رابط مباشر (اختياري)
    st.session_state.profile["avatar_url"] = col1.text_input(
        "Avatar URL (optional)",
        value=st.session_state.profile.get("avatar_url", ""),
        placeholder="https://example.com/me.png",
    )

    # رفع صورة وتخزينها مؤقتًا (Base64) ليقرأها API عند الحفظ
    up = col1.file_uploader("Upload PNG/JPG", type=["png", "jpg", "jpeg"])
    if up is not None:
        try:
            image = Image.open(up).convert("RGB")
            buf = io.BytesIO()
            image.save(buf, format="PNG")
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            # نخزنها تحت مفتاح مدعوم من الـ API
            st.session_state.profile["avatar_b64"] = f"data:image/png;base64,{b64}"
            st.success("✅ Image loaded (will be saved to API)")
        except Exception as e:
            st.error(f"Failed to process image: {e}")

    # المعاينة
    with col2:
        st.markdown("**Preview**")
        # لو عندنا base64، استخدمه أولاً (أحدث من url)
        b64_src = st.session_state.profile.get("avatar_b64")
        if b64_src:
            st.image(b64_src, caption="Uploaded (pending save)", use_column_width=True)
        else:
            url_src = _resolve_image_source(st.session_state.profile.get("avatar_url"))
            if url_src:
                st.image(url_src, caption="From URL", use_column_width=True)
            else:
                st.caption("No image yet")

    # لا نرجّع شيء — نحدّث profile داخل session_state
