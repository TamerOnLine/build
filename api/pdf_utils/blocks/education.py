from __future__ import annotations
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors
from ..config import *
from ..labels import t
from ..icons import get_section_icon, draw_heading_with_icon
from ..text import draw_par
from .base import Frame, RenderContext
from .registry import register

class EducationBlock:
    BLOCK_ID = "education"

    def render(self, c, frame: Frame, data: dict, ctx: RenderContext) -> float:
        items = [str(b).strip() for b in (data.get("items") or []) if str(b).strip()]
        if not items: return frame.y

        title = (data.get("title") or t("professional_training", ctx.get("ui_lang") or UI_LANG))
        y = draw_heading_with_icon(
            c=c, x=frame.x, y=frame.y, title=title, icon=get_section_icon("professional_training"),
            font="Helvetica-Bold", size=HEADING_SIZE, color=HEADING_COLOR,
            underline_w=frame.w, rule_color=RIGHT_SEC_RULE_COLOR, rule_width=RIGHT_SEC_RULE_WIDTH,
            gap_below=GAP_AFTER_HEADING / 2,
        )
        y -= RIGHT_SEC_RULE_TO_TEXT_GAP

        for block in items:
            parts = [ln.strip() for ln in block.splitlines() if ln.strip()]
            if not parts: continue

            c.setFont("Helvetica-Bold", TEXT_SIZE); c.setFillColor(EDU_TITLE_COLOR)
            c.drawString(frame.x, y, parts[0])
            y -= EDU_BLOCK_TITLE_GAP_BELOW

            for ln in parts[1:]:
                if ln.startswith(("http://", "https://")):
                    font_name = "Helvetica-Oblique"
                    c.setFont(font_name, PROJECT_LINK_TEXT_SIZE); c.setFillColor(HEADING_COLOR)
                    c.drawString(frame.x, y, ln)
                    tw  = pdfmetrics.stringWidth(ln, font_name, PROJECT_LINK_TEXT_SIZE)
                    asc = pdfmetrics.getAscent(font_name)/1000.0*PROJECT_LINK_TEXT_SIZE
                    dsc = abs(pdfmetrics.getDescent(font_name))/1000.0*PROJECT_LINK_TEXT_SIZE
                    c.linkURL(ln, (frame.x, y - dsc, frame.x + tw, y + asc*0.2), relative=0, thickness=0)
                    y -= EDU_TEXT_LEADING
                else:
                    c.setFont("Helvetica", RIGHT_SEC_TEXT_SIZE); c.setFillColor(colors.black)
                    y = draw_par(c, frame.x, y, [ln], "Helvetica", RIGHT_SEC_TEXT_SIZE,
                                 frame.w, "left", False, EDU_TEXT_LEADING)
            y -= RIGHT_SEC_SECTION_GAP
        return y

register(EducationBlock())

