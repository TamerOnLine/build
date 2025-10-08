from __future__ import annotations

import os, sys

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st
import json
import base64
import requests

st.set_page_config(page_title="Resume Builder", page_icon="", layout="wide")
st.title("Resume Builder Streamlit")

# ============================================================

# ============================================================
try:
    from st_app.core.api_client import (
        api_generate_pdf,
        build_payload,
        normalize_theme_name,
        choose_layout_inline,
        inject_headshot_into_layout,  
    )
    from st_app.core.schema import ensure_profile_schema
    from st_app.ui.sidebar import render_sidebar
    from st_app.ui.tab_basic import render as render_basic
    from st_app.ui.tab_contact import render as render_contact
    from st_app.ui.tab_skills import render as render_skills
    from st_app.ui.tab_languages import render as render_languages
    from st_app.ui.tab_projects import render as render_projects
    from st_app.ui.tab_education import render as render_education
    from st_app.ui.tab_summary import render as render_summary

    try:
        from st_app.ui.tab_headshot import render as render_headshot
        HAS_HEADSHOT = True
    except Exception:
        HAS_HEADSHOT = False

except Exception as e:
    st.error("Import error in app.py")
    st.exception(e)
    st.stop()

# ============================================================

# ============================================================
settings = render_sidebar()

# ============================================================

# ============================================================
if "profile" not in st.session_state:
    st.session_state.profile = ensure_profile_schema({})

# ============================================================

# ============================================================
tab_defs = [
    ("Basic Info", render_basic),
    ("Contact", render_contact),
    ("Skills", render_skills),
    ("Languages", render_languages),
    ("Projects", render_projects),
    ("Education", render_education),
    ("Summary", render_summary),
]
if HAS_HEADSHOT:
    tab_defs.append(("Headshot", render_headshot))

tabs = st.tabs([t for t, _ in tab_defs])

for (title, render_fn), tab in zip(tab_defs, tabs):
    with tab:
        st.session_state.profile = render_fn(st.session_state.profile)

# ============================================================

# ============================================================
st.markdown("---")
col_gen, col_dbg = st.columns([2, 1])

with col_gen:
    st.subheader("Generate PDF")
    if st.button("Generate", type="primary", key="btn_generate"):
        try:
            layout_inline = choose_layout_inline(settings.get("layout_file"))

            try:
                layout_inline = inject_headshot_into_layout(
                    layout_inline, st.session_state.get("photo_bytes")
                )
            except Exception:
                pass

            payload = build_payload(
                theme_name=normalize_theme_name(
                    settings.get("theme_name") or "default.theme.json"
                ),
                ui_lang=settings.get("ui_lang") or "en",
                rtl_mode=bool(settings.get("rtl_mode")),
                profile=ensure_profile_schema(st.session_state.profile),
                layout_inline=layout_inline,
            )

            st.write(
                "[CLIENT] theme:",
                payload["theme_name"],
                "| layout:",
                settings.get("layout_file"),
            )

            pdf_bytes = api_generate_pdf(
                settings.get("base_url") or "http://127.0.0.1:8000", payload
            )

            b64 = base64.b64encode(pdf_bytes).decode("ascii")
            st.download_button(
                "Download PDF",
                pdf_bytes,
                "resume.pdf",
                "application/pdf",
                key="btn_download_pdf",
            )
            with st.expander("Preview (experimental)"):
                st.markdown(
                    f'<iframe src="data:application/pdf;base64,{b64}" '
                    'style="width:100%;height:80vh;border:none;"></iframe>',
                    unsafe_allow_html=True,
                )
            st.success("✅ PDF generated successfully.")

        except Exception as e:
            st.error("Generation failed:")
            st.exception(e)

# ============================================================

# ============================================================
with col_dbg:
    st.subheader("Debug")
    try:
        if st.checkbox("Show outgoing payload", key="chk_dbg_payload"):
            li = choose_layout_inline(settings.get("layout_file"))
            st.code(
                json.dumps(
                    build_payload(
                        theme_name=normalize_theme_name(
                            settings.get("theme_name") or "default.theme.json"
                        ),
                        ui_lang=settings.get("ui_lang") or "en",
                        rtl_mode=bool(settings.get("rtl_mode")),
                        profile=ensure_profile_schema(st.session_state.profile),
                        layout_inline=li,
                    ),
                    ensure_ascii=False,
                    indent=2,
                ),
                language="json",
            )
    except Exception as e:
        st.warning("Debug payload error:")
        st.exception(e)

