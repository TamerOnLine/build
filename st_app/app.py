# st_app/app.py
from __future__ import annotations
import sys, os, json
import streamlit as st

# ============================================================
# ✅ السماح بالعمل سواء شغّلت من الجذر أو من داخل st_app/
# ============================================================
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(APP_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

# ============================================================
# Tabs (واجهات الحقول) + API helpers
# ============================================================
try:
    # عند التشغيل من الجذر (e.g., D:\build)
    from st_app.ui.tab_summary import render as tab_summary
    from st_app.ui.tab_skills import render as tab_skills
    from st_app.ui.tab_contact import render as tab_contact
    from st_app.ui.tab_projects import render as tab_projects
    from st_app.ui.tab_education import render as tab_education
    from st_app.ui.tab_headshot import render as tab_headshot

    from st_app.core.api_client import (
        build_payload,              # لطلب توليد PDF
        api_generate_pdf,           # استدعاء واجهة التوليد
        save_profile,               # حفظ البروفايل
        build_profile_payload,      # تنظيف/تطبيع الحمولة قبل الحفظ
        normalize_theme_name,       # تطبيع اسم الثيم
        choose_layout_inline,       # اختيار/تحميل تخطيط JSON (اختياري)
        inject_headshot_into_layout # حقن صورة في التخطيط (اختياري)
    )
except ModuleNotFoundError:
    # عند التشغيل من داخل st_app/ مباشرة
    from ui.tab_summary import render as tab_summary
    from ui.tab_skills import render as tab_skills
    from ui.tab_contact import render as tab_contact
    from ui.tab_projects import render as tab_projects
    from ui.tab_education import render as tab_education
    from ui.tab_headshot import render as tab_headshot

    from core.api_client import (
        build_payload,
        api_generate_pdf,
        save_profile,
        build_profile_payload,
        normalize_theme_name,
        choose_layout_inline,
        inject_headshot_into_layout
    )

# ============================================================
# إعداد الصفحة
# ============================================================
st.set_page_config(page_title="Resume Builder Streamlit", layout="wide")
st.title("Resume Builder Streamlit")

# ============================================================
# الحالة العامة
# ============================================================
if "profile" not in st.session_state:
    st.session_state.profile = {
        "header":   {"name": "", "title": ""},
        "contact":  {},
        "summary":  [],
        "skills":   [],
        "languages": [],
        "projects": [],
        "education": [],
        "avatar":   None,
    }

if "profile_rev" not in st.session_state:
    st.session_state.profile_rev = 0

# ============================================================
# الشريط الجانبي
# ============================================================
with st.sidebar:
    st.header("Profile Settings")

    profile_name = st.text_input("Profile name (folder)", value="tamer", help="Used as profiles/<name>/")
    theme_input = st.text_input("Theme name", value="aqua-card")
    theme_name = normalize_theme_name(theme_input)

    # رفع صورة (اختياري) لاستخدامها في التوليد/التخطيط
    photo_file = st.file_uploader("Headshot (PNG/JPG)", type=["png", "jpg", "jpeg"], key="sidebar_photo")
    photo_bytes: bytes | None = photo_file.read() if photo_file else None
    if photo_bytes:
        st.image(photo_bytes, caption="Preview", use_column_width=True)

    st.divider()

    # توليد PDF
    if st.button("🧾 Generate PDF", key="gen_pdf_btn"):
        try:
            profile = st.session_state.profile.copy()

            # (اختياري) التخطيط
            layout = choose_layout_inline("")  # ضع مسار JSON لو عندك قوالب
            layout = inject_headshot_into_layout(layout, photo_bytes)

            payload = {
                "theme_name": theme_name,
                "ui_lang": "en",
                "rtl_mode": False,
                "layout": layout,     # {}
                "profile": profile,
            }

            pdf_bytes = api_generate_pdf(payload)
            st.download_button(
                "Download PDF",
                data=pdf_bytes,
                file_name=f"{profile_name}.pdf",
                mime="application/pdf",
                width="stretch"   # بدل use_container_width=True
            )
        except Exception as e:
            st.error(f"PDF generation error: {e}")

# ============================================================
# قسم الاسم والمسمى الوظيفي
# ============================================================
with st.expander("Header (Name & Title)", expanded=True):
    c1, c2 = st.columns(2)
    with c1:
        st.session_state.profile.setdefault("header", {})
        st.session_state.profile["header"]["name"] = st.text_input(
            "Full name",
            value=st.session_state.profile["header"].get("name", ""),
            placeholder="e.g., Tamer Hamad Faour",
            key="header_name",
            width="stretch"
        )
    with c2:
        st.session_state.profile["header"]["title"] = st.text_input(
            "Professional title",
            value=st.session_state.profile["header"].get("title", ""),
            placeholder="e.g., Software Developer",
            key="header_title",
            width="stretch"
        )

# ============================================================
# التبويبات
# ============================================================
tabs = st.tabs(["Summary", "Skills", "Contact", "Projects", "Education", "Headshot"])

with tabs[0]:
    st.session_state.profile = tab_summary(st.session_state.profile)

with tabs[1]:
    st.session_state.profile = tab_skills(st.session_state.profile)

with tabs[2]:
    st.session_state.profile = tab_contact(st.session_state.profile)

with tabs[3]:
    st.session_state.profile = tab_projects(st.session_state.profile)

with tabs[4]:
    st.session_state.profile = tab_education(st.session_state.profile)

with tabs[5]:
    st.session_state.profile = tab_headshot(st.session_state.profile)

# زيادة رقم المراجعة لتوليد مفاتيح فريدة داخل التبويبات
st.session_state.profile_rev += 1

# ============================================================
# Save Profile (بعد التبويبات لضمان تحديث الحالة قبل الإرسال)
# ============================================================
st.divider()
if st.button("💾 Save Profile", key="save_profile_main", type="primary"):
    try:
        payload = build_profile_payload(st.session_state.profile)
        result = save_profile(profile_name, payload)
        st.success(f"Saved ✓ (name: {result.get('name','')})")
    except Exception as e:
        st.error(f"Save failed: {e}")

# ============================================================
# Debug (اختياري)
# ============================================================
with st.expander("Debug: current profile payload", expanded=False):
    st.code(json.dumps(st.session_state.profile, indent=2, ensure_ascii=False), language="json")
