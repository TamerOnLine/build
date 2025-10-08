from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple, Callable
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from .blocks.base import Frame, RenderContext
from .blocks.registry import get as get_block
from .block_aliases import canonicalize

@dataclass
class Column:
    id: str
    x: float
    w: float

@dataclass
class PageSpec:
    width: float
    height: float
    margins: Dict[str, float]  # {top, right, bottom, left} in points

@dataclass
class FlowCursor:
    """Maintains y-position cursor per column."""
    y_by_col: Dict[str, float]

class LayoutEngine:
    """
    Modern rendering engine based on JSON layout (flow/columns/overrides).
    - Renders one block at a time within a specified column.
    - Automatically creates a new page when space runs out.
    - Applies overrides for each block.
    """

    def __init__(
        self,
        canvas: Canvas,
        page: PageSpec,
        columns: Dict[str, Tuple[float, float]],
        theme: Dict[str, Any],
        ui_lang: str,
        rtl_mode: bool,
    ):
        self.c = canvas
        self.page = page
        self.columns: Dict[str, Column] = {
            cid: Column(cid, x, w) for cid, (x, w) in columns.items()
        }
        top_y = self.page.height - self.page.margins.get("top", 22 * mm)
        self.cursor = FlowCursor(y_by_col={cid: top_y for cid in self.columns})
        self.theme = theme or {}
        self.ui_lang = ui_lang
        self.rtl_mode = rtl_mode

    def _split_id(self, raw_id: str) -> Tuple[str, Optional[str]]:
        raw_id = canonicalize(raw_id)
        if ":" in raw_id:
            base, suffix = raw_id.split(":", 1)
            return base, suffix
        return raw_id, None

    def _block_data_for(
        self,
        base_id: str,
        suffix: Optional[str],
        ready: Dict[str, Any],
        conf_data: Optional[Dict[str, Any]],
    ):
        data = ready.get(base_id)
        if data is None:
            data = conf_data
        if suffix and isinstance(data, dict) and suffix in data:
            data = data[suffix]
        if isinstance(data, (list, tuple)):
            data = "\n".join(str(x) for x in data)
        return data or {}

    def _ctx(self) -> RenderContext:
        return {
            "ui_lang": self.ui_lang,
            "rtl_mode": self.rtl_mode,
            "page_top_y": self.page.height - self.page.margins.get("top", 22 * mm),
            "page_h": self.page.height,
            "theme": self.theme,
            "columns": {cid: (col.x, col.w) for cid, col in self.columns.items()},
            "page_conf": {
                "margin_mm": {
                    k: v / mm for k, v in self.page.margins.items()
                }
            },
        }

    def _new_page(self):
        """Start a new page and reset cursors."""
        self.c.showPage()
        top_y = self.page.height - self.page.margins.get("top", 22 * mm)
        for cid in self.columns:
            self.cursor.y_by_col[cid] = top_y

    def _bottom_limit(self) -> float:
        return self.page.margins.get("bottom", 18 * mm)

    def render_flow(
        self,
        flow: List[Dict[str, Any]],
        ready: Dict[str, Any],
        overrides: Dict[str, Any] | None = None,
    ):
        """
        Renders blocks as defined in the flow structure.
        Each flow item defines a column and a list of blocks:
        flow = [
            {"column": "left", "blocks": [ ... ]},
            ...
        ]
        """
        overrides = overrides or {}
        ctx_base = self._ctx()

        for group in (flow or []):
            col_id = group.get("column")
            if col_id not in self.columns:
                col_id = next(iter(self.columns.keys()))
            col = self.columns[col_id]

            for raw in (group.get("blocks") or []):
                blk = {"block_id": raw} if isinstance(raw, str) else dict(raw or {})

                raw_id = blk.get("block_id")
                if not raw_id:
                    continue

                base_id, suffix = self._split_id(raw_id)
                block = get_block(base_id)

                ov = (overrides.get(base_id) or {}) | (overrides.get(raw_id) or {})
                conf_data = ((blk.get("data") or {}) | (ov.get("data") or {})) or None
                frame_dict = (blk.get("frame") or {}) | (ov.get("frame") or {})

                x = float(frame_dict.get("x", col.x))
                w = float(frame_dict.get("w", col.w))
                y = float(frame_dict.get("y", self.cursor.y_by_col[col_id]))
                frame = Frame(x=x, y=y, w=w)

                block_data = self._block_data_for(base_id, suffix, ready, conf_data)

                ctx = dict(ctx_base)
                if suffix:
                    ctx["section"] = suffix

                new_y = block.render(self.c, frame, block_data, ctx)

                if new_y < self._bottom_limit():
                    self._new_page()
                    frame = Frame(x=col.x, y=self.cursor.y_by_col[col_id], w=col.w)
                    new_y = block.render(self.c, frame, block_data, ctx)

                self.cursor.y_by_col[col_id] = new_y

