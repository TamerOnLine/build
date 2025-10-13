from __future__ import annotations

# --- bootstrap for imports ---
from pathlib import Path
import sys

# أضف جذر المشروع إلى sys.path (ليتعرف على st_app كموديول)
ROOT = Path(__file__).resolve().parents[1]  # -> D:\build
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# -----------------------------


import json
from typing import Any, Dict

import streamlit as st

from st_app.ui.tab_summary import render as tab_summary
from st_app.ui.tab_skills import render as tab_skills
from st_app.ui.tab_contact import render as tab_contact
from st_app.ui.tab_projects import render as tab_projects
from st_app.ui.tab_education import render as tab_education
from st_app.ui.tab_headshot import render as tab_headshot

try:
    from st_app.core.api_client import api_generate_pdf
except Exception:
    def api_generate_pdf(payload: Dict[str, Any]) -> bytes:
        raise RuntimeError("Missing api_generate_pdf. Check st_app/core/api_client.py")

try:
    from st_app.core.layout import choose_layout_inline, inject_headshot_into_layout
except Exception:
    def choose_layout_inline(_: str) -> Dict[str, Any] | None:
        return None

    def inject_headshot_into_layout(layout: Dict[str, Any] | None, headshot: bytes | None):
        return layout

def normalize_theme_name(name: str) -> str:
    return (name or "").strip().lower().replace(" ", "-")

def _default_profile() -> Dict[str, Any]:
    return {
        "header": {"name": "", "title": ""},
        "summary": "",
        "skills": [],
        "contact": {
            "email": "",
            "phone": "",
            "website": "",
            "github": "",
            "linkedin": "",
            "location": "",
        },
        "projects": [],
        "education": [],
    }

def ensure_session_state() -> None:
    st.session_state.setdefault("profile", _default_profile())
    st.session_state.setdefault("headshot_bytes", None)
    st.session_state.setdefault("profile_name", "tamer")
    st.session_state.setdefault("theme_name", "aqua-card")

def render_sidebar() -> None:
    from pathlib import Path
    import json

    with st.sidebar:
        st.header("Profile Settings")

        st.session_state.profile_name = st.text_input(
            "Profile name (folder)",
            value=st.session_state.get("profile_name", "tamer"),
            help="Used as profiles/<name>/"
        )

        theme_input = st.text_input(
            "Theme name",
            value=st.session_state.get("theme_name", "aqua-card"),
        )
        st.session_state.theme_name = normalize_theme_name(theme_input)

        st.divider()

        # ====== Save / Load in sidebar ======
        col_s, col_l = st.columns(2)
        with col_s:
            if st.button("💾 Save profile", key="sidebar_save_profile"):
                try:
                    out_dir = Path("profiles") / st.session_state.profile_name
                    out_dir.mkdir(parents=True, exist_ok=True)

                    # إن وُجدت صورة headshot في الجلسة، احفظها كملف ودوّن مرجعها في الـ JSON
                    photo_bytes = st.session_state.get("headshot_bytes")
                    if photo_bytes:
                        (out_dir / "headshot.png").write_bytes(photo_bytes)
                        st.session_state.profile.setdefault("avatar", "headshot.png")

                    (out_dir / "profile.json").write_text(
                        json.dumps(st.session_state.profile, ensure_ascii=False, indent=2),
                        encoding="utf-8"
                    )
                    st.success(f"Saved: {(out_dir / 'profile.json').as_posix()}")
                except Exception as e:
                    st.error(f"Save error: {e}")

        with col_l:
            if st.button("📂 Load profile", key="sidebar_load_profile"):
                try:
                    in_dir = Path("profiles") / st.session_state.profile_name
                    json_fp = in_dir / "profile.json"
                    if json_fp.exists():
                        data = json.loads(json_fp.read_text(encoding="utf-8"))
                        st.session_state.profile = data
                        # إن وُجدت الصورة على القرص، حملها إلى الجلسة لعرضها فورًا
                        avatar = data.get("avatar")
                        if avatar:
                            img_fp = in_dir / avatar
                            if img_fp.exists():
                                st.session_state["headshot_bytes"] = img_fp.read_bytes()
                        st.success(f"Loaded: {json_fp.as_posix()}")
                    else:
                        st.warning(f"File not found: {json_fp.as_posix()}")
                except Exception as e:
                    st.error(f"Load error: {e}")

        st.divider()

        # ====== Generate PDF ======
        if st.button("📄 Generate PDF", key="gen_pdf_btn"):
            try:
                profile = st.session_state.profile.copy()
                photo_bytes: bytes | None = st.session_state.get("headshot_bytes")

                layout = choose_layout_inline("")   # استخدم التخطيط الافتراضي إن لم يوجد
                layout = inject_headshot_into_layout(layout, photo_bytes)

                payload = {
                    "theme_name": st.session_state.theme_name,
                    "ui_lang": "en",
                    "rtl_mode": False,
                    "layout": layout,
                    "profile": profile,
                }

                pdf_bytes = api_generate_pdf(payload)
                st.download_button(
                    "Download PDF",
                    data=pdf_bytes,
                    file_name=f"{st.session_state.profile_name}.pdf",
                    mime="application/pdf",
                )
            except Exception as e:
                st.error(f"PDF generation error: {e}")

def main() -> None:
    ensure_session_state()
    render_sidebar()

    st.title("Resume Builder")

    tabs = st.tabs([
        "Header", "Summary", "Skills", "Contact", "Projects", "Education", "Headshot"
    ])

    with tabs[0]:
        st.subheader("Header")
        st.session_state.profile.setdefault("header", {})
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.profile["header"]["name"] = st.text_input(
                "Full name",
                value=st.session_state.profile["header"].get("name", ""),
                placeholder="e.g., Tamer Hamad Faour",
                key="header_name",
            )
        with c2:
            st.session_state.profile["header"]["title"] = st.text_input(
                "Professional title",
                value=st.session_state.profile["header"].get("title", ""),
                placeholder="e.g., Software Developer",
                key="header_title",
            )

    with tabs[1]:
        st.session_state.profile = tab_summary(st.session_state.profile)
    with tabs[2]:
        st.session_state.profile = tab_skills(st.session_state.profile)
    with tabs[3]:
        st.session_state.profile = tab_contact(st.session_state.profile)
    with tabs[4]:
        st.session_state.profile = tab_projects(st.session_state.profile)
    with tabs[5]:
        st.session_state.profile = tab_education(st.session_state.profile)
    with tabs[6]:
        st.session_state.profile = tab_headshot(st.session_state.profile)

    st.divider()


    with st.expander("Debug — profile JSON"):
        st.code(
            json.dumps(st.session_state.profile, ensure_ascii=False, indent=2),
            language="json",
        )

if __name__ == "__main__":
    main()