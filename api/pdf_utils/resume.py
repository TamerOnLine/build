from __future__ import annotations

from io import BytesIO
from typing import Dict, Any, List, Tuple, Optional

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import mm

from .blocks.base import Frame, RenderContext
from .blocks.registry import get as get_block
from .data_utils import build_ready_from_profile
from .config import UI_LANG
from .theme_loader import load_and_apply
from .block_aliases import canonicalize
from .data_utils import build_ready_from_profile  
try:
    from .data_mapper import map_profile_to_ready  
except Exception:
    _HAS_MAPPER = False


from .engine import LayoutEngine, PageSpec
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.units import mm


# Default page size and margins
PAGE_W, PAGE_H = A4
LEFT_MARGIN = 18 * mm
RIGHT_MARGIN = 18 * mm
TOP_MARGIN = 22 * mm
BOTTOM_MARGIN = 18 * mm

_PAGE_SIZES = {
    "A4": A4,
    "Letter": LETTER,
}


def build_resume_pdf(
    data: Optional[Dict[str, Any]] = None,
    *,
    layout_plan: Optional[List[Dict[str, Any]]] = None,
    ready: Optional[Dict[str, Any]] = None,
    ui_lang: Optional[str] = None,
    rtl_mode: Optional[bool] = None,
    theme_name: Optional[str] = None,
    theme: Optional[str] = None,
    page: Optional[Dict[str, Any]] = None,
) -> bytes:
    """Build a resume PDF from modern or legacy inputs.

    This function supports two usage modes:

    * **Modern usage**: Provide a ``data`` mapping that includes keys such as
      ``profile``, ``ui_lang``, ``rtl_mode``, ``theme_name``, and
      ``layout_inline``. The function resolves the layout, applies defaults, and
      renders the PDF.
    * **Legacy usage**: Provide ``layout_plan`` and ``ready`` along with optional
      ``ui_lang``, ``rtl_mode``, and ``theme_name``. Fallback layout/columns are
      used when not supplied.

    Args:
        data: Modern input mapping containing profile and configuration values.
        layout_plan: Legacy layout plan (list of section dictionaries).
        ready: Legacy preprocessed data mapping to render.
        ui_lang: UI language code (e.g., "en").
        rtl_mode: Whether right-to-left rendering is enabled.
        theme_name: Name of the theme to load and apply.
        theme: Optional alias for ``theme_name``; if provided and
            ``theme_name`` is missing, this value is used.
        page: Page configuration mapping (e.g., size, margins).

    Returns:
        bytes: The rendered PDF as a byte string.

    Notes:
        - Logic is preserved from the original implementation; only formatting
          and documentation were adjusted to comply with PEP 8 and documentation
          standards.
        - This function relies on external helpers such as ``load_and_apply``,
          ``map_profile_to_ready``, ``_resolve_layout_columns_page_from_inline``,
          ``_apply_page_defaults``, and ``_render_pdf``.
    """
    if theme and not theme_name:
        theme_name = theme

    # -------- Modern usage --------
    if data is not None:
        ui = data.get("ui_lang") or UI_LANG
        rtl = bool(data.get("rtl_mode"))
        profile = data.get("profile") or {}
        tn = theme_name or data.get("theme_name") or "default"
        theme_dict = load_and_apply(tn)

        # Mapping layer (Mapper) with fallback.
        if _HAS_MAPPER:
            li = data.get("layout_inline") or {}
            rd, map_warnings = map_profile_to_ready(
                profile,
                ui_lang=ui,
                rtl_mode=rtl,
                map_rules_override=li.get("map_rules") or {},
            )
            if map_warnings:
                print("[Mapper] warnings:", map_warnings)
        else:
            rd = build_ready_from_profile(profile)

        plan, cols, page_conf = _resolve_layout_columns_page_from_inline(data)
        _apply_page_defaults(page_conf)

        return _render_pdf(
            plan,
            rd,
            ui_lang=ui,
            rtl_mode=rtl,
            columns=cols,
            theme=theme_dict,
            page=page_conf,
        )

    # -------- Legacy usage --------
    ui = ui_lang or UI_LANG
    rtl = bool(rtl_mode)
    rd = ready or {}
    plan = layout_plan or _fallback_layout()
    cols = _fallback_columns()
    tn = theme_name or "default"
    theme_dict = load_and_apply(tn)
    page_conf = page or {}

    _apply_page_defaults(page_conf)

    return _render_pdf(
        plan,
        rd,
        ui_lang=ui,
        rtl_mode=rtl,
        columns=cols,
        theme=theme_dict,
        page=page_conf,
    )


def _render_pdf(
    layout_plan: List[Dict[str, Any]] | Dict[str, Any],
    ready: Dict[str, Any],
    *,
    ui_lang: str,
    rtl_mode: bool,
    columns: Dict[str, Tuple[float, float]],
    theme: Optional[Dict[str, Any]] = None,
    page: Optional[Dict[str, Any]] = None,
) -> bytes:
    """
    Render the PDF. If layout_plan is a dict with flow => use modern engine.
    Otherwise fall back to legacy list-based rendering.
    """
    # ---------------------------
    # Modern engine (flow-based)
    # ---------------------------
    if isinstance(layout_plan, dict) and layout_plan.get("flow"):
        pagesize = _resolve_page_size(page)
        buf = BytesIO()
        c = canvas.Canvas(buf, pagesize=pagesize)

        # Page margins in points
        margins = {
            "top":    _get_margin(page, "top",    default_px=TOP_MARGIN),
            "right":  _get_margin(page, "right",  default_px=RIGHT_MARGIN),
            "bottom": _get_margin(page, "bottom", default_px=BOTTOM_MARGIN),
            "left":   _get_margin(page, "left",   default_px=LEFT_MARGIN),
        }
        ps = PageSpec(width=pagesize[0], height=pagesize[1], margins=margins)

        engine = LayoutEngine(
            canvas=c,
            page=ps,
            columns=columns,  # {col_id: (x, w)}
            theme=theme or {},
            ui_lang=ui_lang,
            rtl_mode=rtl_mode,
        )

        engine.render_flow(
            flow=layout_plan.get("flow") or [],
            ready=ready,
            overrides=layout_plan.get("overrides") or {},
        )

        c.showPage()
        c.save()
        return buf.getvalue()

    # ---------------------------
    # Legacy block list engine
    # ---------------------------
    if isinstance(layout_plan, dict):
        layout_plan = layout_plan.get("layout", [])

    fixed_plan: List[Dict[str, Any]] = []
    for it in layout_plan or []:
        if isinstance(it, dict) and it.get("block_id"):
            fixed_plan.append(dict(it))
        elif isinstance(it, str) and it.strip():
            fixed_plan.append({"block_id": it.strip()})
        else:
            print(f"[WARN] Skipping invalid layout item in _render: {it!r}")

    for it in fixed_plan:
        it["block_id"] = canonicalize(it["block_id"])

    pagesize = _resolve_page_size(page)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=pagesize)

    ctx: RenderContext = {
        "ui_lang": ui_lang,
        "rtl_mode": rtl_mode,
        "page_top_y": pagesize[1] - _get_margin(page, "top", default_px=TOP_MARGIN),
        "page_h": pagesize[1],
        "theme": theme or {},
        "columns": columns,
        "page_conf": page or {},
    }

    for block_conf in fixed_plan:
        try:
            raw_id = block_conf.get("block_id")
            if isinstance(raw_id, str) and ":" in raw_id:
                base_id, suffix = (raw_id.split(":", 1) + [None])[:2]
            else:
                base_id, suffix = raw_id, None

            block = get_block(base_id)
            frame_dict = block_conf.get("frame") or {}
            frame = Frame(
                x=float(frame_dict.get("x", _get_margin(page, "left", default_px=LEFT_MARGIN))),
                y=float(frame_dict.get("y", pagesize[1] - _get_margin(page, "top", default_px=TOP_MARGIN))),
                w=float(
                    frame_dict.get(
                        "w",
                        pagesize[0]
                        - _get_margin(page, "left", default_px=LEFT_MARGIN)
                        - _get_margin(page, "right", default_px=RIGHT_MARGIN),
                    )
                ),
            )

            block_data = ready.get(base_id)
            if block_data is None:
                block_data = block_conf.get("data")

            if suffix and isinstance(block_data, dict) and suffix in block_data:
                block_data = block_data[suffix]

            if isinstance(block_data, (list, tuple)):
                block_data = "\n".join(str(x) for x in block_data)

            ctx_local = dict(ctx)
            if suffix:
                ctx_local["section"] = suffix

            new_y = block.render(c, frame, block_data or {}, ctx_local)
            frame.y = new_y

        except Exception as e:
            print(f"[WARN] Block '{block_conf.get('block_id') if isinstance(block_conf, dict) else block_conf}' failed: {e}")
            continue

    c.showPage()
    c.save()
    return buf.getvalue()


# ============================================================
#              Layout/Columns/Page resolution helpers
# ============================================================
def _resolve_layout_columns_page_from_inline(data: Dict[str, Any]):
    """
    Extracts layout_plan, columns, and page_conf from data["layout_inline"],
    or returns fallbacks if not present.

    Args:
        data (Dict[str, Any]): Input data dictionary containing layout_inline.

    Returns:
        Tuple[List[Dict[str, Any]], Dict[str, Tuple[float, float]], Dict[str, Any]]:
            A tuple containing the layout plan, column definitions, and page config.
    """
    li = data.get("layout_inline") or {}


    # 1) Drawing plan: flow > layout
    plan: List[Dict[str, Any]] = []
    flow = li.get("flow") or []
    if flow:
        flat: List[Dict[str, Any]] = []
        for grp in flow:
            for b in grp.get("blocks") or []:
                if isinstance(b, str):
                    flat.append({"block_id": b})
                elif isinstance(b, dict) and b.get("block_id"):
                    flat.append(dict(b))
        plan = flat
    else:
        layout_old = li.get("layout") or []
        for it in layout_old:
            if isinstance(it, str):
                plan.append({"block_id": it})
            elif isinstance(it, dict) and it.get("block_id"):
                plan.append(dict(it))

    # 2) Columns
    cols_def = li.get("columns") or []
    columns = _columns_from_percentages(cols_def) if cols_def else _fallback_columns()

    # 3) Page configuration
    page_conf = li.get("page") or {}
    return plan, columns, page_conf


def _columns_from_percentages(cols_def: List[Dict[str, Any]]) -> Dict[str, Tuple[float, float]]:
    """
    Converts definitions like:
        [{"id": "left", "width": "33%"}, {"id": "right", "width": "67%"}]
    into a dictionary: {id: (x, w)} with point units based on page margins.

    Args:
        cols_def (List[Dict[str, Any]]): List of column definitions with width in percent.

    Returns:
        Dict[str, Tuple[float, float]]: Mapping of column IDs to (x, width) in points.
    """
    total_w = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    x_cursor = LEFT_MARGIN
    out: Dict[str, Tuple[float, float]] = {}

    for c in cols_def:
        cid = str(c.get("id") or "").strip() or f"col_{len(out)+1}"
        w_str = str(c.get("width") or "100%").strip()
        if w_str.endswith("%"):
            try:
                pct = float(w_str[:-1]) / 100.0
            except Exception:
                pct = 1.0
        else:
            pct = 1.0

        w = total_w * pct
        out[cid] = (x_cursor, w)

        gutter_mm = float(c.get("gutter_mm") or 0) * mm
        x_cursor += w + gutter_mm

    return out if out else _fallback_columns()


def _apply_page_defaults(page_conf: Dict[str, Any]) -> None:
    """
    Apply default values to the page configuration if not already set.

    Args:
        page_conf (Dict[str, Any]): Page configuration dictionary to modify.
    """
    if page_conf is None:
        page_conf = {}
    page_conf.setdefault("size", "A4")
    page_conf.setdefault("orientation", "portrait")
    page_conf.setdefault("margin_mm", {"top": 22, "right": 18, "bottom": 18, "left": 18})
    page_conf.setdefault("gutter_mm", 6)


def _resolve_page_size(page_conf: Optional[Dict[str, Any]]):
    """
    Resolve the page size tuple based on the given configuration.

    Args:
        page_conf (Optional[Dict[str, Any]]): Page configuration dictionary.

    Returns:
        Tuple[float, float]: Width and height of the page.
    """
    if not page_conf:
        return A4
    size = str(page_conf.get("size") or "A4")
    orient = str(page_conf.get("orientation") or "portrait")
    base = _PAGE_SIZES.get(size, A4)
    if orient == "landscape":
        return base[1], base[0]
    return base


def _get_margin(page_conf: Optional[Dict[str, Any]], side: str, *, default_px: float) -> float:
    """
    Retrieve the margin value (in points) for a given side.

    Args:
        page_conf (Optional[Dict[str, Any]]): Page configuration dictionary.
        side (str): Margin side ('top', 'right', 'bottom', or 'left').
        default_px (float): Default margin value in points.

    Returns:
        float: Margin value in points.
    """
    if not page_conf:
        return default_px
    m = page_conf.get("margin_mm") or {}
    val = m.get(side)
    try:
        return float(val) * mm if val is not None else default_px
    except Exception:
        return default_px
    

# ============================================================
#                        FALLBACKS
# ============================================================
def _fallback_layout() -> List[Dict[str, Any]]:
    """
    Provides a basic fallback layout plan when no layout JSON is provided.

    Returns:
        List[Dict[str, Any]]: A list of layout block configurations.
    """
    return [
        {
            "block_id": "header_name",
            "frame": {
                "x": LEFT_MARGIN,
                "y": PAGE_H - TOP_MARGIN,
                "w": PAGE_W - LEFT_MARGIN - RIGHT_MARGIN,
            },
            "data": {"centered": True, "highlight_bg": "#E0F2FE", "box_h_mm": 30},
        },
        {
            "block_id": "key_skills",
            "frame": {"x": LEFT_MARGIN, "y": PAGE_H - 60 * mm, "w": 80 * mm},
        },
        {
            "block_id": "projects",
            "frame": {"x": 110 * mm, "y": PAGE_H - 60 * mm, "w": 85 * mm},
        },
    ]

def _fallback_columns() -> Dict[str, Tuple[float, float]]:
    """
    Provides default left/right column widths for blocks relying on columns.

    Returns:
        Dict[str, Tuple[float, float]]: A dictionary mapping column IDs to (x, width).
    """
    total_w = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN
    left_w = total_w * 0.4
    right_w = total_w * 0.55
    return {
        "left": (LEFT_MARGIN, left_w),
        "right": (LEFT_MARGIN + left_w + 5 * mm, right_w),
    }

