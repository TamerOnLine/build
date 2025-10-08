from __future__ import annotations
from reportlab.lib import colors
from ..config import (
    LEFT_SEC_TITLE_TOP_GAP, LEFT_SEC_HEADING_SIZE, HEADING_COLOR,
    LEFT_SEC_RULE_COLOR, LEFT_SEC_RULE_WIDTH, LEFT_SEC_TITLE_BOTTOM_GAP,
    LEFT_SEC_RULE_TO_LIST_GAP, LEFT_SEC_TEXT_SIZE, LEFT_SEC_TEXT_X_OFFSET,
    LEFT_SEC_BULLET_X_OFFSET, LEFT_SEC_BULLET_RADIUS, LEFT_SEC_LINE_GAP,
)
from ..labels import t
from ..config import UI_LANG
from ..icons import get_section_icon, draw_heading_with_icon
from ..text import wrap_text
from .base import Frame, RenderContext
from .registry import register

class KeySkillsBlock:
    BLOCK_ID = "key_skills"

    def render(self, c, frame: Frame, data: dict, ctx: RenderContext) -> float:
        title = (data.get("title") or t("key_skills", ctx.get("ui_lang") or UI_LANG))
        skills = [str(s).strip() for s in (data.get("skills") or []) if str(s).strip()]
        if not skills: return frame.y
        y = frame.y - LEFT_SEC_TITLE_TOP_GAP
        y = draw_heading_with_icon(
            c=c, x=frame.x, y=y, title=title, icon=get_section_icon("key_skills"),
            font="Helvetica-Bold", size=LEFT_SEC_HEADING_SIZE, color=HEADING_COLOR,
            underline_w=frame.w, rule_color=LEFT_SEC_RULE_COLOR, rule_width=LEFT_SEC_RULE_WIDTH,
            gap_below=LEFT_SEC_TITLE_BOTTOM_GAP / 2,
        )
        y -= LEFT_SEC_RULE_TO_LIST_GAP
        c.setFont("Helvetica", LEFT_SEC_TEXT_SIZE); c.setFillColor(colors.black)
        max_w = frame.w - (LEFT_SEC_TEXT_X_OFFSET + 2)
        for sk in skills:
            for i, ln in enumerate(wrap_text(sk, "Helvetica", LEFT_SEC_TEXT_SIZE, max_w)):
                if i == 0:
                    c.circle(frame.x + LEFT_SEC_BULLET_X_OFFSET, y + 3, LEFT_SEC_BULLET_RADIUS, stroke=1, fill=1)
                c.drawString(frame.x + LEFT_SEC_TEXT_X_OFFSET, y, ln)
                y -= LEFT_SEC_LINE_GAP
        return y

register(KeySkillsBlock())

