# streamlit/ui/sidebar.py
from __future__ import annotations

import json
import base64
import streamlit as st

from core.paths import THEMES_DIR, LAYOUTS_DIR
from core.schema import ensure_profile_schema
from core.io_utils import list_json_names
from core import api_client as api  # عميل الـ API

from st_app.config.ui_defaults import (
    DEFAULT_API_BASE,
    UI_LANG_OPTIONS,
    DEFAULT_THEME_FALLBACK,
)

def _clean_name(name: str) -> str:
    """أزل .json وافرغ المسافات وحدد اسمًا صالحًا للحفظ في API."""
    n = (name or "").strip()
    if n.lower().endswith(".json"):
        n = n[:-5]
    return n or "my_profile"


def _apply_photo_b64_to_session(profile: dict) -> None:
    """
    إن وُجد photo_b64 داخل البروفايل المحمَّل/المستورَد،
    حوّله إلى photo_bytes في حالة الجلسة لعرضه فورًا واستخدامه في PDF.
    """
    b64 = profile.get("photo_b64")
    if not b64:
        return
    try:
        st.session_state.photo_bytes = base64.b64decode(b64)
        st.session_state.photo_mime = "image/png"
    except Exception:
        st.session_state.photo_bytes = None
        st.session_state.photo_mime = None


def render_sidebar() -> dict:
    """
    يُعيد إعدادات:
    { base_url, ui_lang, rtl_mode, theme_name, layout_file }
    """
    with st.sidebar:
        st.header("Controls")

        # ===== إعداد عنوان الـ API =====
        base_no_api = st.text_input("API Base URL", value=DEFAULT_API_BASE, key="api_base")

        api.BASE = f"{base_no_api.rstrip('/')}/api"  # مزامنة BASE في عميل الـAPI

        # ===== إعدادات الطباعة =====
        ui_lang = st.selectbox("UI Language", UI_LANG_OPTIONS, index=0, key="ui_lang")
        rtl_mode = st.toggle("RTL mode", value=(ui_lang == "ar"), key="rtl_mode")

        theme_files = list_json_names(THEMES_DIR)
        theme_name = st.selectbox("Theme", theme_files or [DEFAULT_THEME_FALLBACK], key="theme_name")

        layout_files = list_json_names(LAYOUTS_DIR)
        layout_file = st.selectbox(
            "Layout",
            ["(none)"] + layout_files,
            index=1 if layout_files else 0,
            key="layout_file",
            help="اختر ملف لايـاوت من /layouts. إن كان (none) سيُرسل بدون inline layout.",
        )

        st.markdown("---")
        st.subheader("Profiles (via API)")

        # ===== قائمة الأسماء من API =====
        try:
            existing_profiles = api.list_profiles()  # أسماء بدون .json
        except Exception as e:
            st.error(f"API list error: {e}")
            existing_profiles = []

        col_p_load, col_p_save = st.columns(2)

        # ---- Load ----
        with col_p_load:
            selected_profile = st.selectbox(
                "Select profile",
                ["(none)"] + existing_profiles,
                index=0,
                key="selected_profile_api",
            )
            if st.button("Load Profile", key="btn_load_profile_api"):
                if selected_profile and selected_profile != "(none)":
                    try:
                        loaded = api.load_profile(selected_profile)
                        st.session_state.profile = ensure_profile_schema(loaded)

                        # لو الصورة محفوظة داخل JSON كـ base64، ضَعها في الجلسة لعرضها مباشرة
                        _apply_photo_b64_to_session(st.session_state.profile)

                        # إجبار إعادة تحميل الودجتس (keys مربوطة بـ profile_rev)
                        st.session_state.profile_rev = st.session_state.get("profile_rev", 0) + 1
                        st.rerun()
                    except Exception as e:
                        st.error(f"Load failed: {e}")

        # ---- Save ----
        with col_p_save:
            profile_name_in = st.text_input("Save as (name only)", value="my_profile", key="save_profile_as_api")
            if st.button("Save Profile", key="btn_save_profile_api"):
                try:
                    name = _clean_name(profile_name_in)
                    payload = ensure_profile_schema(st.session_state.get("profile", {}))

                    # لو في صورة في الجلسة، خزّنها داخل البروفايل كـ photo_b64
                    if st.session_state.get("photo_bytes"):
                        payload["photo_b64"] = base64.b64encode(st.session_state["photo_bytes"]).decode("ascii")

                    api.save_profile(name, payload)
                    st.success(f"Saved (API): {name}.json")
                except Exception as e:
                    st.error(f"Save failed: {e}")

        st.markdown("---")
        # ---- Import JSON ----
        up = st.file_uploader("Import profile (.json)", type=["json"], key="uploader_profile_api")
        if up is not None and st.button("Import now", key="btn_import_now_api"):
            try:
                imported = json.loads(up.getvalue().decode("utf-8"))
                st.session_state.profile = ensure_profile_schema(imported)

                # لو JSON فيه photo_b64، أعِد بنائها في الجلسة
                _apply_photo_b64_to_session(st.session_state.profile)

                # أجبر تحديث الودجتس
                st.session_state.profile_rev = st.session_state.get("profile_rev", 0) + 1
                st.success("Imported profile applied to the form.")
                st.rerun()
            except Exception as e:
                st.error(f"Import failed: {e}")

        # ---- Export JSON ----
        if st.button("Export current as JSON", key="btn_export_json_api"):
            st.download_button(
                "Download JSON",
                data=json.dumps(
                    ensure_profile_schema(st.session_state.get("profile", {})),
                    ensure_ascii=False,
                    indent=2,
                ).encode("utf-8"),
                file_name="profile_export.json",
                mime="application/json",
                key="download_export_json_api",
            )

    return {
        "base_url": base_no_api,  # بدون /api — يُستخدم لاحقًا للتوليد
        "ui_lang": ui_lang,
        "rtl_mode": rtl_mode,
        "theme_name": theme_name,
        "layout_file": layout_file,
    }
