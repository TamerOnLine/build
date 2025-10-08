from __future__ import annotations

import json
import traceback
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from api.schemas import GenerateFormRequest
from ..pdf_utils.resume import build_resume_pdf

# Try importing block registry
try:
    from ..pdf_utils.blocks.registry import get as get_block
except Exception:
    def get_block(_: str):
        return None

# Try importing validators
try:
    from api.schemas.validators import assert_valid_layout, assert_valid_theme
except Exception:
    def assert_valid_layout(_: dict) -> None: ...
    def assert_valid_theme(_: dict) -> None: ...


router = APIRouter(prefix="", tags=["generate"])

PROJECT_ROOT = Path(__file__).resolve().parents[2]
THEMES_DIR = PROJECT_ROOT / "themes"
LAYOUTS_DIR = PROJECT_ROOT / "layouts"


# ------------------------------- helpers -------------------------------

def _prefer_fixed(path: Path) -> Path:
    """Use .fixed version of a file if it exists, else return the original path."""
    fixed = path.with_suffix(path.suffix + ".fixed")
    return fixed if fixed.exists() else path

def _safe_json_read(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"[Warn] Failed to read JSON: {path} -> {e}")
        return {}

def _normalize_layout_list(items: List[Any]) -> List[Dict[str, Any]]:
    """Normalize layout items to a list of block_id dictionaries."""
    out: List[Dict[str, Any]] = []
    for it in (items or []):
        if isinstance(it, str) and it.strip():
            out.append({"block_id": it.strip()})
        elif isinstance(it, dict) and it.get("block_id"):
            out.append(it)
        else:
            print(f"[Warn] Skipping invalid layout item: {it!r}")
    return out

def _normalize_layout_value(layout_value: Any) -> Dict[str, Any]:
    """Normalize layout structure to include page, columns, flow, layout, and overrides."""
    layout_value = layout_value or {}
    return {
        "page": layout_value.get("page") or {},
        "columns": layout_value.get("columns") or [],
        "flow": layout_value.get("flow") or [],
        "layout": _normalize_layout_list(layout_value.get("layout") or []),
        "overrides": layout_value.get("overrides") or {},
    }

def _build_layout_inline_from_theme(theme_name: Optional[str]) -> Dict[str, Any]:
    """Build inline layout by reading from a theme file."""
    theme_name = theme_name or "default"
    p = _prefer_fixed(THEMES_DIR / f"{theme_name}.theme.json")
    theme = _safe_json_read(p)
    try:
        assert_valid_theme(theme)
    except Exception as e:
        print("[Warn] theme validation:", e)
    lay = theme.get("layout") or {}
    return {
        "page": theme.get("page") or lay.get("page") or {},
        "columns": lay.get("columns") or [],
        "flow": lay.get("flow") or [],
        "layout": _normalize_layout_list(lay.get("layout") or []),
        "overrides": lay.get("overrides") or {},
    }

def _load_layout_inline(layout_name: Optional[str]) -> Dict[str, Any]:
    """Load and normalize an external layout file."""
    if not layout_name:
        return {}
    p = _prefer_fixed(LAYOUTS_DIR / f"{layout_name}.layout.json")
    obj = _safe_json_read(p)
    try:
        assert_valid_layout(obj)
    except Exception as e:
        print("[Warn] layout validation:", e)
    return _normalize_layout_value(obj)

def _merge_layouts(theme_inline: Dict[str, Any], layout_inline: Dict[str, Any]) -> Dict[str, Any]:
    """Merge theme and layout structures, giving priority to the layout."""
    merged = dict(theme_inline or {})
    for key in ("page", "columns", "flow", "layout", "overrides"):
        if key in layout_inline and layout_inline[key]:
            merged[key] = layout_inline[key]
        elif key not in merged:
            merged[key] = [] if key in ("columns", "flow", "layout") else {}
    if merged.get("flow"):
        merged["layout"] = []
    return merged

def _extract_wanted_block_ids(merged_inline: Dict[str, Any]) -> List[str]:
    """Extract block_ids used in the layout flow or layout list."""
    wanted: List[str] = []
    if merged_inline.get("flow"):
        for grp in (merged_inline["flow"] or []):
            for b in (grp.get("blocks") or []):
                if isinstance(b, str):
                    wanted.append(b)
                elif isinstance(b, dict) and b.get("block_id"):
                    wanted.append(b["block_id"])
    else:
        for it in (merged_inline.get("layout") or []):
            if isinstance(it, str):
                wanted.append(it)
            elif isinstance(it, dict) and it.get("block_id"):
                wanted.append(it["block_id"])
    return wanted

def _preflight(merged_inline: dict, profile: dict) -> None:
    """Run pre-checks for required blocks and missing profile data."""
    wanted_raw = _extract_wanted_block_ids(merged_inline)
    wanted_base = [(bid.split(":")[0] if isinstance(bid, str) else "") for bid in wanted_raw]

    not_registered: List[str] = [b for b in wanted_base if b and get_block(b) is None]

    key_map = {
        "header_name": "header",
        "contact_info": "contact",
        "key_skills": "skills",
        "languages": "languages",
        "projects": "projects",
        "education": "education",
        "social_links": "social_links",
        "avatar_circle": "avatar",
        "links_inline": "contact",
        "text_section": "summary",
    }
    missing_data: List[str] = [
        raw for raw in wanted_raw
        if key_map.get(raw.split(":")[0]) not in (profile or {})
    ]

    print(f"[PREFLIGHT] blocks: {wanted_raw}")
    if not_registered:
        print(f"[PREFLIGHT] Warning: not registered: {sorted(set(not_registered))}")
    if missing_data:
        print(f"[PREFLIGHT] Info: profile has no data for: {sorted(set(missing_data))}")

def _apply_overrides_to_layout(merged_inline: Dict[str, Any]) -> Dict[str, Any]:
    """Apply data/frame overrides to each block based on block_id."""
    overrides = merged_inline.get("overrides") or {}
    if merged_inline.get("flow"):
        new_flow = []
        for grp in merged_inline["flow"]:
            new_blocks = []
            for b in grp.get("blocks", []):
                blk = {"block_id": b} if isinstance(b, str) else dict(b)
                bid = blk.get("block_id", "")
                ov = overrides.get(bid.split(":")[0]) or overrides.get(bid) or {}
                if ov.get("data"):
                    blk["data"] = {**(blk.get("data") or {}), **ov["data"]}
                if ov.get("frame"):
                    blk["frame"] = {**(blk.get("frame") or {}), **ov["frame"]}
                new_blocks.append(blk)
            new_flow.append({"column": grp.get("column"), "blocks": new_blocks})
        merged_inline["flow"] = new_flow
    else:
        new_layout = []
        for b in (merged_inline.get("layout") or []):
            blk = {"block_id": b} if isinstance(b, str) else dict(b)
            bid = blk.get("block_id", "")
            ov = overrides.get(bid.split(":")[0]) or overrides.get(bid) or {}
            if ov.get("data"):
                blk["data"] = {**(blk.get("data") or {}), **ov["data"]}
            if ov.get("frame"):
                blk["frame"] = {**(blk.get("frame") or {}), **ov["frame"]}
            new_layout.append(blk)
        merged_inline["layout"] = new_layout
    return merged_inline


# ------------------------------- route -------------------------------

@router.post("/generate-form-simple")
async def generate_form_simple(req: GenerateFormRequest):
    """
    Generate a PDF resume from provided profile, theme, and layout configuration.

    Args:
        req (GenerateFormRequest): The request containing profile, layout, and theme info.

    Returns:
        StreamingResponse: The generated PDF resume.
    """
    try:
        print(f"[REQ] theme='{req.theme_name}', layout='{req.layout_name}'")

        prof = dict(req.profile or {})
        print("[Debug] PROFILE keys:", list(prof.keys()))

        theme_inline = _build_layout_inline_from_theme(req.theme_name)
        layout_inline = _load_layout_inline(req.layout_name) if req.layout_name else {}
        merged_inline = _merge_layouts(theme_inline, layout_inline)
        merged_inline = _apply_overrides_to_layout(merged_inline)

        flow_len = len(merged_inline.get("flow") or [])
        cols_len = len(merged_inline.get("columns") or [])
        print(f"[Info] Layout has flow={flow_len} columns={cols_len}")

        _preflight(merged_inline, prof)

        data: Dict[str, Any] = {
            "ui_lang": (req.ui_lang or prof.get("ui_lang") or "en"),
            "rtl_mode": bool(req.rtl_mode if req.rtl_mode is not None else prof.get("rtl_mode", False)),
            "profile": prof,
            "theme_name": req.theme_name or "default",
            "layout_inline": merged_inline,
        }

        pdf_bytes = build_resume_pdf(data=data)

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f'inline; filename="resume-{req.theme_name or "default"}.pdf"'},
        )

    except HTTPException:
        raise
    except Exception as e:
        print("[Error] /generate-form-simple:")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {e}")


@router.get("/healthz")
def healthz():
    """Health check endpoint."""
    return {
        "ok": True,
        "themes_dir": str(THEMES_DIR),
        "layouts_dir": str(LAYOUTS_DIR),
    }

