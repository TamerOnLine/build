"""FastAPI application for generating resume PDFs.

Exposes:
- GET  /healthz
- POST /generate-form-simple : build PDF from profile + (optional) layout/theme
- /api/profiles/*            : save/load JSON profiles (via profiles router)
"""

from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ValidationError, field_validator

# 1) Register fonts (side-effect)
from api.pdf_utils import fonts  # noqa: F401
from api.pdf_utils.builder import build_resume_pdf
from api.pdf_utils.mapper import profile_to_overrides
from api.routes import profiles as profiles_routes  # /api/profiles/*
from api.pdf_utils.schema import ensure_profile_schema  # ✅ أضفنا هذا الاستيراد

log = logging.getLogger("resume.api")
logging.basicConfig(level=logging.INFO)

APP_ROOT = Path(__file__).resolve().parent.parent
THEMES_DIR = APP_ROOT / "themes"
LAYOUTS_DIR = APP_ROOT / "layouts"

app = FastAPI(title="Resume API")

# ─────────────────────────────────────────────────────────────
# CORS (tighten in production)
# ─────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = [
    "http://localhost:8501",  # Streamlit (local)
    "http://127.0.0.1:8501",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

# Routes for profiles CRUD
app.include_router(profiles_routes.router, prefix="/api")


def normalize_theme_name(tn: Optional[str]) -> str:
    """Normalize an incoming theme name (drop '.theme.json' if present)."""
    if not tn:
        return "default"
    return tn[:-11] if tn.endswith(".theme.json") else tn


def coerce_summary(profile: Dict[str, Any]) -> None:
    """If summary is a stringified list, convert it to a single joined string."""
    val = profile.get("summary")
    if isinstance(val, str):
        s = val.strip()
        if s.startswith("[") and s.endswith("]"):
            try:
                import ast

                lst = ast.literal_eval(s)
                if isinstance(lst, list):
                    profile["summary"] = " ".join(str(x) for x in lst if x)
            except Exception:
                pass


def _decode_headshots(node: Any) -> None:
    """Recursively convert avatar_circle.data.photo_b64 -> photo_bytes."""
    if isinstance(node, dict):
        if (node.get("block_id") == "avatar_circle") and isinstance(node.get("data"), dict):
            d = node["data"]
            b64 = d.get("photo_b64")
            if b64 and not d.get("photo_bytes"):
                try:
                    d["photo_bytes"] = base64.b64decode(b64.encode("ascii"))
                except Exception:
                    d["photo_bytes"] = None
        for v in list(node.values()):
            _decode_headshots(v)
    elif isinstance(node, list):
        for it in node:
            _decode_headshots(it)


def _deep_merge_fill_missing(dst: dict, src: dict) -> dict:
    """
    Merge without overwriting existing keys in dst (fill-only-missing).
    - If both values are dicts, recurse.
    - Otherwise, copy src[k] only if k not in dst.
    """
    for k, v in (src or {}).items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge_fill_missing(dst[k], v)
        elif k not in dst:
            dst[k] = v
    return dst


def _safe_read_layout_by_name(layout_name: str) -> Dict[str, Any]:
    """Read a JSON layout by name safely (prevent path traversal)."""
    candidate = (LAYOUTS_DIR / layout_name).resolve()
    if not str(candidate).startswith(str(LAYOUTS_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid layout path.")
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Layout not found: {layout_name}")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to read layout: {exc}")


class GeneratePayload(BaseModel):
    theme_name: Optional[str] = Field(default=None, description="Theme name or 'x.theme.json'")
    theme: Optional[str] = Field(default=None, description="Legacy alias for theme_name")
    ui_lang: str = Field(default="en")
    rtl_mode: bool = Field(default=False)

    profile: Dict[str, Any] = Field(default_factory=dict)
    layout_inline: Optional[Dict[str, Any]] = None
    layout_name: Optional[str] = None

    @field_validator("ui_lang")
    @classmethod
    def _trim_lang(cls, v: str) -> str:
        return (v or "en").strip() or "en"

    def effective_theme_name(self) -> str:
        return normalize_theme_name(self.theme_name or self.theme)


@app.on_event("startup")
def _startup() -> None:
    try:
        fonts.register_all_fonts()
        log.info("Fonts registered.")
    except Exception as exc:
        log.warning("Font registration failed: %s", exc)


@app.get("/healthz")
def healthz() -> Dict[str, bool]:
    return {"ok": True}


@app.post("/generate-form-simple")
def generate_form_simple(payload: Dict[str, Any]) -> Response:
    """Generate a resume PDF from the provided payload."""
    try:
        args = GeneratePayload.model_validate(payload)
    except ValidationError as ve:
        raise HTTPException(status_code=422, detail=json.loads(ve.json()))

    # Build base data for PDF builder
    data: Dict[str, Any] = {
        "theme_name": args.effective_theme_name(),
        "ui_lang": args.ui_lang,
        "rtl_mode": bool(args.rtl_mode),
        "profile": args.profile or {},
    }

    # ✅ Normalize profile data before PDF build
    data["profile"] = ensure_profile_schema(data["profile"])

    # Resolve layout_inline (prefer inline, else by name)
    layout_inline = args.layout_inline
    if not layout_inline and isinstance(args.layout_name, str) and args.layout_name.strip():
        layout_inline = _safe_read_layout_by_name(args.layout_name.strip())

    if not layout_inline:
        layout_inline = {"flow": []}

    # Derive overrides from profile & merge (fill-only-missing)
    ov_from_profile = profile_to_overrides(data["profile"])
    layout_inline.setdefault("overrides", {})
    layout_inline["overrides"] = _deep_merge_fill_missing(layout_inline["overrides"], ov_from_profile)

    # Decode headshots (photo_b64 -> photo_bytes)
    _decode_headshots(layout_inline)

    # Coerce summary if it's a stringified list
    if isinstance(data["profile"], dict):
        coerce_summary(data["profile"])

    # Attach layout
    data["layout_inline"] = layout_inline

    # Log details
    flow = layout_inline.get("flow", [])
    blocks_count = sum(len(x.get("blocks", [])) for x in flow) if isinstance(flow, list) else 0
    log.info("PDF request: theme=%s blocks=%s", data["theme_name"], blocks_count)

    # Build PDF
    try:
        pdf_bytes = build_resume_pdf(data=data)
    except Exception as exc:
        log.exception("PDF build failed")
        raise HTTPException(status_code=500, detail=f"PDF build failed: {exc}")

    headers = {
        "Content-Disposition": 'inline; filename="resume.pdf"',
        "Cache-Control": "no-store",
    }
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
