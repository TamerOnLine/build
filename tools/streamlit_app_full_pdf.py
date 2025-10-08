#!/usr/bin/env python3
# streamlit_app_full_pdf.py
# Streamlit UI to generate a full resume PDF from your project's real profile data.
#
# Modes:
#   - API mode (recommended): uses st_app.core.api_client.api_generate_pdf()
#   - Direct mode (fallback): calls api.pdf_utils.builder.build_resume_pdf() without HTTP
#
# Run:
#   streamlit run streamlit_app_full_pdf.py
#
from __future__ import annotations
import base64
import json
from pathlib import Path
import streamlit as st

# ====== Try to load your project's clients (API + schema utils) ======
HAS_API = False
HAS_DIRECT = False
try:
    from st_app.core.api_client import api_generate_pdf, build_payload, normalize_theme_name
    from st_app.core.schema import ensure_profile_schema  # if exists in your repo
    HAS_API = True
except Exception:
    api_generate_pdf = None
    build_payload = None
    normalize_theme_name = lambda x: x or "aqua-card"

try:
    from api.pdf_utils.fonts import register_all_fonts
    from api.pdf_utils.builder import build_resume_pdf
    HAS_DIRECT = True
except Exception:
    pass

st.set_page_config(page_title="Full Resume PDF", page_icon="📄", layout="wide")
st.title("📄 Generate Full Resume PDF")

# ====== Sidebar: Mode & Inputs ======
st.sidebar.header("Settings")
mode = st.sidebar.radio("Generation mode", ["API (FastAPI)", "Direct (no server)"], index=0 if HAS_API else 1)
profile_path = st.sidebar.text_input("Profile JSON path", value="profiles/my_profile.json")
layout_choice = st.sidebar.text_input("Layout", value="two-column.layout.json" if mode.startswith("API") else "layouts/two-column.layout.json")
theme_name = st.sidebar.text_input("Theme name", value="aqua-card")
ui_lang = st.sidebar.selectbox("UI language", options=["en", "ar", "de"], index=0)
rtl_mode = st.sidebar.checkbox("RTL mode", value=(ui_lang == "ar"))
gen_btn = st.sidebar.button("🚀 Generate PDF")

# ====== Load Profile ======
root = Path.cwd()
profile_file = (root / profile_path).resolve()
if not profile_file.exists():
    st.error(f"Profile not found: {profile_file}")
    st.stop()

try:
    profile = json.loads(profile_file.read_text(encoding="utf-8"))
except Exception as e:
    st.error(f"Failed to parse profile JSON: {e}")
    st.stop()

# Optional: validate/normalize profile if helper exists
if 'ensure_profile_schema' in globals() and callable(ensure_profile_schema):
    profile = ensure_profile_schema(profile)

st.subheader("Profile source")
st.code(str(profile_file), language="bash")

with st.expander("Preview profile JSON", expanded=False):
    st.json(profile)

# ====== PDF Generation ======
pdf_bytes = None
if gen_btn:
    try:
        if mode.startswith("API"):
            if not HAS_API:
                st.error("API client not available. Switch to Direct mode or ensure st_app.core.api_client is importable.")
            else:
                # API mode uses layout_name (server must have that file under layouts/)
                payload = {
                    "theme_name": normalize_theme_name(theme_name),
                    "ui_lang": ui_lang,
                    "rtl_mode": bool(rtl_mode),
                    "profile": profile,
                    "layout_name": layout_choice,  # e.g., "two-column.layout.json"
                }
                pdf_bytes = api_generate_pdf(**payload)
        else:
            if not HAS_DIRECT:
                st.error("Direct builder not available. Ensure api.pdf_utils.builder is importable.")
            else:
                # Direct mode loads the layout file locally
                layout_path = (root / layout_choice).resolve()
                if not layout_path.exists():
                    st.error(f"Layout file not found: {layout_path}")
                else:
                    from json import loads
                    layout = loads(layout_path.read_text(encoding="utf-8"))
                    register_all_fonts()
                    data = {
                        "theme_name": theme_name,
                        "ui_lang": ui_lang,
                        "rtl_mode": bool(rtl_mode),
                        "profile": profile,
                        "layout_inline": layout,
                    }
                    pdf_bytes = build_resume_pdf(data=data)
    except Exception as e:
        st.error(f"PDF generation failed: {e}")

# ====== Display + Download ======
if pdf_bytes:
    st.success("PDF generated successfully!")
    st.write(f"Size: {len(pdf_bytes):,} bytes")

    # Inline PDF preview
    b64_pdf = base64.b64encode(pdf_bytes).decode("ascii")
    st.markdown(
        f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="100%" height="800px"></iframe>',
        unsafe_allow_html=True,
    )

    st.download_button(
        "⬇️ Download PDF",
        data=pdf_bytes,
        file_name="resume_full.pdf",
        mime="application/pdf",
    )
else:
    st.info("Set your options on the left and click **Generate PDF**.")
