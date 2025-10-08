# api/pdf_utils/blocks/text_section.py
from __future__ import annotations
from reportlab.lib import colors
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.units import mm

from ..config import *
from ..text import draw_par
from ..icons import draw_heading_with_icon
from .base import Frame, RenderContext
from .registry import register


class TextSectionBlock:
    """
    ط¨ظ„ظˆظƒ ط¹ط§ظ… ظ„ط¹ط±ط¶ ط£ظ‚ط³ط§ظ… ظ†طµظٹط© ظ…ط«ظ„ (summary, about, objective, ...)

    - ظٹط¯ط¹ظ… ط§ظ„طµظٹط؛ ط§ظ„طھط§ظ„ظٹط©:
        "text_section:summary"
        "text_section:about"
        "text_section:objective"
    - ظٹظ‚ط±ط£ ظ…ط­طھظˆط§ظ‡ ظ…ظ†:
        profile["summary"] ط£ظˆ profile["about"] ط£ظˆ data["text"]
    """

    BLOCK_ID = "text_section"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        section = (data.get("section") or data.get("key") or "summary").strip()

        # ًںڈ·ï¸ڈ طھط­ط¯ظٹط¯ ط§ظ„ط¹ظ†ظˆط§ظ† ط§ظ„ط§ظپطھط±ط§ط¶ظٹ ط­ط³ط¨ ظ†ظˆط¹ ط§ظ„ظ‚ط³ظ…
        title_map = {
            "summary": "Professional Summary",
            "about": "About Me",
            "objective": "Career Objective",
        }
        title = data.get("title") or title_map.get(section, section.title())

        # ًں“„ طھط­ط¯ظٹط¯ ظ…ط­طھظˆظ‰ ط§ظ„ظ†طµ (list ط£ظˆ str)
        lines = data.get(section) or data.get("lines") or data.get("text") or []
        if isinstance(lines, str):
            lines = [lines]
        if not lines:
            return frame.y

        # ًںژ¨ ط±ط³ظ… ط§ظ„ط¹ظ†ظˆط§ظ† ظ…ط¹ ط®ط· طھط­طھ ط§ظ„ط¹ظ†ظˆط§ظ† (ظ†ظپط³ ظ†ط¸ط§ظ… Projects)
        y = draw_heading_with_icon(
            c=c,
            x=frame.x,
            y=frame.y,
            title=title,
            icon=None,
            font="Helvetica-Bold",
            size=RIGHT_SEC_HEADING_SIZE,
            color=HEADING_COLOR,
            underline_w=frame.w,
            rule_color=RIGHT_SEC_RULE_COLOR,
            rule_width=RIGHT_SEC_RULE_WIDTH,
            gap_below=GAP_AFTER_HEADING / 2,
        )
        y -= RIGHT_SEC_RULE_TO_TEXT_GAP

        # âœچï¸ڈ ط±ط³ظ… ط§ظ„ظ†طµظˆطµ ظپظ‚ط±ط© ظپظ‚ط±ط©
        c.setFont("Helvetica", RIGHT_SEC_TEXT_SIZE)
        c.setFillColor(colors.black)
        y = draw_par(
            c,
            frame.x,
            y,
            lines,
            "Helvetica",
            RIGHT_SEC_TEXT_SIZE,
            frame.w,
            "left",
            False,
            BODY_LEADING,
            RIGHT_SEC_PARA_GAP,
        )

        y -= RIGHT_SEC_SECTION_GAP
        return y


# âœ… ط§ظ„طھط³ط¬ظٹظ„ ط§ظ„ظٹط¯ظˆظٹ (ظ†ظپط³ ط£ط³ظ„ظˆط¨ ProjectsBlock ظˆ SkillsGridBlock)
register(TextSectionBlock())

