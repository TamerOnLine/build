# api/pdf_utils/blocks/left_panel_bg.py
from __future__ import annotations
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from .base import Frame, RenderContext
from .registry import register
from ..config import LEFT_BG, LEFT_BORDER

class LeftPanelBG:
    """
    يرسم خلفية العمود الأيسر ممتدة من أعلى الصفحة إلى أسفلها ضمن عرض العمود.
    data:
      - pad_mm : هامش داخلي بسيط (افتراضي 4)
      - bg     : لون الخلفية (إلا إذا عُرِّف LEFT_BG في config)
      - border : لون الحدود (اختياري؛ يعتمد LEFT_BORDER إن وجد)
    """
    BLOCK_ID = "left_panel_bg"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        # الإعدادات
        pad_mm  = float((data or {}).get("pad_mm") or 4.0)
        pad     = pad_mm * mm
        bg_hex  = (data or {}).get("bg") or LEFT_BG or "#F7F8FA"
        br_hex  = (data or {}).get("border") or LEFT_BORDER  # قد يكون None

        # أبعاد الرسم
        x      = frame.x
        w      = frame.w
        top_y  = frame.y
        page_h = float(ctx.get("page_h") or (297 * mm))  # A4 fallback
        h      = max(0.0, page_h - (2 * pad))

        # الرسم
        c.saveState()
        try:
            c.setFillColor(colors.HexColor(bg_hex))
        except Exception:
            c.setFillColor(colors.HexColor("#F7F8FA"))

        # استخدم roundRect من ReportLab مباشرة لتجنب اختلاف تواقيع util
        # ملاحظة: radius بوحدات النقاط (ليس mm)
        radius = 6  # نقاط
        c.roundRect(x, top_y - h, w, h, radius, stroke=0, fill=1)

        # خط حدود اختياري
        if br_hex:
            try:
                c.setStrokeColor(colors.HexColor(br_hex))
            except Exception:
                c.setStrokeColor(colors.HexColor("#E3E6EA"))
            c.setLineWidth(0.6)
            # خط رفيع على حافة العمود اليسرى
            c.line(x, top_y - h, x, top_y)

        c.restoreState()
        # لا نغيّر Y؛ الخلفية فقط
        return frame.y

# تسجيل بنفس أسلوب النظام
register(LeftPanelBG())


