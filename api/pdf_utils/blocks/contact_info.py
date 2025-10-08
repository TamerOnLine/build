from __future__ import annotations
from ..config import (
    LEFT_SEC_TITLE_TOP_GAP, LEFT_SEC_HEADING_SIZE, HEADING_COLOR,
    LEFT_SEC_RULE_COLOR, LEFT_SEC_RULE_WIDTH, LEFT_SEC_TITLE_BOTTOM_GAP,
    LEFT_SEC_RULE_TO_LIST_GAP, LEFT_TEXT_SIZE, LEFT_LINE_GAP,
)
from ..labels import t
from ..config import UI_LANG
from ..icons import ICON_PATHS, draw_icon_line, draw_heading_with_icon
from .base import Frame, RenderContext
from .registry import register

class ContactInfoBlock:
    BLOCK_ID = "contact_info"

    def render(self, c, frame: Frame, data: dict, ctx: RenderContext) -> float:
        # data: { "title"?: str, "items": {label: value, ...} }
        title = (data.get("title") or t("personal_info", ctx.get("ui_lang") or UI_LANG))
        items = data.get("items") or {}
        y = frame.y - LEFT_SEC_TITLE_TOP_GAP
        y = draw_heading_with_icon(
            c=c, x=frame.x, y=y, title=title, icon=None,
            font="Helvetica-Bold", size=LEFT_SEC_HEADING_SIZE, color=HEADING_COLOR,
            underline_w=frame.w, rule_color=LEFT_SEC_RULE_COLOR, rule_width=LEFT_SEC_RULE_WIDTH,
            gap_below=LEFT_SEC_TITLE_BOTTOM_GAP / 2,
        )
        y -= LEFT_SEC_RULE_TO_LIST_GAP
        for label, value in items.items():
            icon = ICON_PATHS.get((label or "").lower()) or ICON_PATHS.get(label)
            y = draw_icon_line(c, frame.x, y, (value or ""), icon=icon,
                               font="Helvetica", size=LEFT_TEXT_SIZE, line_gap=LEFT_LINE_GAP)
        return y

register(ContactInfoBlock())

