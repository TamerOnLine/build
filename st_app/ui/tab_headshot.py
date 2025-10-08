# streamlit/ui/tab_headshot.py
from __future__ import annotations
import io
from io import BytesIO
from typing import Optional, Tuple
import base64

import streamlit as st
from PIL import Image, ImageOps, ImageDraw

from st_app.config.ui_defaults import (
    MAX_FILE_MB, MAX_DIM, DEFAULT_EXPORT, DEFAULT_PHOTO_CIRCLE_MASK
)


def _exif_transpose(img: Image.Image) -> Image.Image:
    """
    Respect camera EXIF orientation (auto-rotate). No-op if not present.
    """
    try:
        return ImageOps.exif_transpose(img)
    except Exception:
        return img

def _square_center_crop(img: Image.Image) -> Image.Image:
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    return img.crop((left, top, left + side, top + side))

def _cap_dims(img: Image.Image, max_dim: int = MAX_DIM) -> Image.Image:
    w, h = img.size
    if max(w, h) <= max_dim:
        return img
    scale = max_dim / float(max(w, h))
    new = (max(1, int(w * scale)), max(1, int(h * scale)))
    return img.resize(new, Image.LANCZOS)

def _circle_mask(size: int) -> Image.Image:
    """Create an RGBA circular mask of given size (filled)."""
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, size, size), fill=255)
    return mask

def _to_png_bytes(img: Image.Image) -> bytes:
    """
    Save image as PNG with no metadata. Keeps alpha if present.
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()

def _b64_from_bytes(b: bytes) -> str:
    return base64.b64encode(b).decode("ascii")

def _valid_size(file) -> Tuple[bool, str]:
    if file is None:
        return True, ""
    # Some uploaders expose file.size; if not, read buffer and check length.
    size_bytes = getattr(file, "size", None)
    if size_bytes is None:
        try:
            pos = file.tell()
            file.seek(0, 2)
            size_bytes = file.tell()
            file.seek(pos)
        except Exception:
            size_bytes = None
    if size_bytes is not None and size_bytes > MAX_FILE_MB * 1024 * 1024:
        return False, f"File is too large ({size_bytes/1024/1024:.1f} MB). Max is {MAX_FILE_MB} MB."
    return True, ""

def render(profile: dict) -> dict:
    st.subheader("Headshot / Photo")
    rev = st.session_state.get("profile_rev", 0)

    # Controls row
    left, mid, right = st.columns([1, 1, 1])
    with left:
        up = st.file_uploader(
            "Upload (PNG/JPG/WebP)",
            type=["png", "jpg", "jpeg", "webp"],
            key=f"photo_uploader_{rev}",
        )
    with mid:
        size_px = st.slider(
            "Output size (px)",
            128, 1024, st.session_state.get("photo_export_size", DEFAULT_EXPORT),
            step=64,
            key=f"photo_export_size_{rev}",
            help="This is the size that will be embedded in the PDF."
        )
        st.session_state["photo_export_size"] = size_px
    with right:
        circle = st.toggle(
            "Circle mask (transparent)",
            value=st.session_state.get("photo_circle_mask", DEFAULT_PHOTO_CIRCLE_MASK),
            key=f"photo_circle_{rev}",
            help="If on, the exported PNG keeps a round transparent background."
        )
        st.session_state["photo_circle_mask"] = circle

    # If user hits Clear, wipe session photo
    clear_col, _ = st.columns([1, 3])
    with clear_col:
        if st.button("Clear photo", use_container_width=True, key=f"photo_clear_{rev}"):
            for k in ("photo_bytes", "photo_mime", "avatar_b64"):
                st.session_state.pop(k, None)
            # also clear any previously uploaded reference to prevent auto reload
            st.session_state.pop(f"photo_uploader_{rev}", None)
            st.session_state["profile_rev"] = rev + 1
            st.info("Photo cleared.")
            return profile

    # Determine source image
    img: Optional[Image.Image] = None

    if up is not None:
        ok, msg = _valid_size(up)
        if not ok:
            st.error(msg)
            return profile
        try:
            img = Image.open(up)
            img = _exif_transpose(img)
            # Convert to RGBA for consistent masking/alpha
            img = img.convert("RGBA")
            img = _cap_dims(img, MAX_DIM)
        except Exception:
            st.error("Cannot open the uploaded image. Please try a different file.")
            img = None

    elif st.session_state.get("photo_bytes"):
        try:
            img = Image.open(BytesIO(st.session_state["photo_bytes"])).convert("RGBA")
        except Exception:
            img = None

    # Layout previews
    col1, col2, col3 = st.columns([1, 1, 1])
    if img is not None:
        with col1:
            st.caption("Original")
            st.image(img, width='stretch')

        cropped = _square_center_crop(img)
        if circle:
            # Apply circular mask onto transparent canvas
            s = min(cropped.size)
            mask = _circle_mask(s)
            circ = Image.new("RGBA", (s, s), (0, 0, 0, 0))
            circ.paste(cropped.resize((s, s), Image.LANCZOS), (0, 0), mask)
            square_for_export = circ
        else:
            square_for_export = cropped

        with col2:
            st.caption("Square crop")
            st.image(square_for_export, width='stretch')

        preview = square_for_export.resize((size_px, size_px), Image.LANCZOS)
        with col3:
            st.caption("Export size")
            st.image(preview, caption=f"{size_px}×{size_px}", width='stretch')

        # Save: always store square PNG (keeps alpha for circle)
        out_bytes = _to_png_bytes(preview)
        st.session_state.photo_bytes = out_bytes
        st.session_state.photo_mime = "image/png"
        st.session_state.avatar_b64 = _b64_from_bytes(out_bytes)

        # Also mirror into profile so server-side mappers can pick it up
        profile.setdefault("avatar_b64", st.session_state.avatar_b64)

        st.success("Photo ready. It will be embedded in the PDF automatically.")
    else:
        st.info("Upload a square-ish image for best results. We’ll auto square-crop and (optionally) round-mask it.")

    return profile
