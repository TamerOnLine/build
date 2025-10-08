from __future__ import annotations
from io import BytesIO
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from ..config import LEFT_BORDER, CARD_PAD
from .base import Frame, RenderContext
from .registry import register

class AvatarCircleBlock:
    BLOCK_ID = "avatar_circle"

    def render(self, c, frame: Frame, data: dict, ctx: RenderContext) -> float:
        # data: { "photo_bytes": bytes, "max_d_mm"?: float (ط§ظپطھط±ط§ط¶ظٹ 42) }
        photo_bytes = data.get("photo_bytes")
        if not photo_bytes:
            return frame.y  # ظ„ط§ ط´ظٹط،

        max_d = float(data.get("max_d_mm", 42)) * mm
        d = min(frame.w, max_d)
        r = d / 2.0
        cx = frame.x + frame.w / 2.0
        cy = frame.y - r
        ix = cx - r
        iy = cy - r

        try:
            img = ImageReader(BytesIO(photo_bytes))
            c.saveState()
            p = c.beginPath()
            p.circle(cx, cy, r)
            c.clipPath(p, stroke=0, fill=0)
            c.drawImage(img, ix, iy, width=d, height=d, preserveAspectRatio=True, mask="auto")
            c.restoreState()
            c.setStrokeColor(LEFT_BORDER)
            c.setLineWidth(1)
            c.circle(cx, cy, r)
            new_y = iy - 6 * mm
            return new_y
        except Exception:
            return frame.y

register(AvatarCircleBlock())

