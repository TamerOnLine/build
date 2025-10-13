from __future__ import annotations

import base64

import streamlit as st

def _to_b64(data: bytes) -> str:
    """
    Convert bytes to a base64-encoded UTF-8 string.

    Args:
        data (bytes): Image data in bytes.

    Returns:
        str: Base64-encoded string representation of the image.
    """
    return base64.b64encode(data).decode("utf-8")

def render(profile: dict) -> dict:
    """
    Render the 'Profile Picture / Headshot' tab in the Streamlit app.

    Args:
        profile (dict): The current profile data.

    Returns:
        dict: Updated profile dictionary with headshot avatar as base64 string.
    """
    st.subheader("Profile Picture / Headshot")

    rev = st.session_state.get("profile_rev", 0)

    current_b64 = profile.get("avatar") or None
    if current_b64:
        try:
            st.image(
                base64.b64decode(current_b64),
                caption="Current photo",
                use_column_width=True,
            )
        except Exception:
            st.warning("Stored avatar is not a valid base64 image. You can replace it below.")

    uploaded = st.file_uploader(
        "Upload image (PNG/JPG)",
        type=["png", "jpg", "jpeg"],
        key=f"headshot_uploader_{rev}",
    )

    new_b64 = None
    if uploaded:
        data = uploaded.read()
        st.image(data, caption="New photo (preview)", use_column_width=True)
        new_b64 = _to_b64(data)

    c1, c2, _ = st.columns([1, 1, 6])
    with c1:
        if st.button("💾 Save photo", key=f"headshot_save_{rev}"):
            if new_b64:
                profile["avatar"] = new_b64
                st.success("Photo saved to profile.")
            else:
                st.info("No new image selected.")
    with c2:
        if st.button("\u274C Clear photo", key=f"headshot_clear_{rev}"):
            profile["avatar"] = None
            st.experimental_rerun()

    return profile
