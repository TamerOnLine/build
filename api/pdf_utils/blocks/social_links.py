from __future__ import annotations
from typing import Any, Dict, List, Tuple
from reportlab.pdfbase import pdfmetrics
from reportlab.lib import colors

from ..config import (
    LEFT_SEC_TITLE_TOP_GAP, LEFT_SEC_HEADING_SIZE, HEADING_COLOR,
    LEFT_SEC_RULE_COLOR, LEFT_SEC_RULE_WIDTH, LEFT_SEC_TITLE_BOTTOM_GAP,
    LEFT_SEC_RULE_TO_LIST_GAP, LEFT_TEXT_SIZE, LEFT_LINE_GAP,
)
from ..labels import t
from ..config import UI_LANG
from ..icons import get_section_icon, draw_heading_with_icon, ICON_PATHS
from ..text import wrap_text
from .. import social  # ظ†ط³طھط®ط¯ظ… ط£ط¯ظˆط§طھ ط§ظ„طھظ†ط¸ظٹظپ/ط§ظ„ط¨ظ†ط§ط، ظ…ظ† social.py ظ„ظˆ ظ…طھط§ط­ط©
from .base import Frame, RenderContext
from .registry import register

class SocialLinksBlock:
    """
    طھط¹ط±ط¶ ط±ظˆط§ط¨ط· ط§ط¬طھظ…ط§ط¹ظٹط© ط¨طµظٹط؛ط© ظ…ط±طھط¨ط© ظ…ط¹ ط£ظٹظ‚ظˆظ†ط§طھ + ط±ظˆط§ط¨ط· ظ‚ط§ط¨ظ„ط© ظ„ظ„ظ†ظ‚ط±.
    data طھط¯ط¹ظ… ط´ظƒظ„ظٹظ†:
      A) {"items": [{"label":"GitHub","value":"TamerOnLine"}, {"label":"LinkedIn","value":"tameronline"}, ...]}
      B) {"github":"TamerOnLine","linkedin":"tameronline","website":"https://..."}  (ط³ظٹظڈط­ظˆظ‘ظژظ„ ط¯ط§ط®ظ„ظٹظ‹ط§ ط¥ظ„ظ‰ items)
    ظٹظ…ظƒظ† طھظ…ط±ظٹط± title ط§ط®طھظٹط§ط±ظٹظ‹ط§.
    """
    BLOCK_ID = "social_links"

    def _normalize(self, data: Dict[str, Any]) -> List[Tuple[str, str, str]]:
        items_in = data.get("items")
        triples: List[Tuple[str, str, str]] = []

        if items_in and isinstance(items_in, list):
            for it in items_in:
                label = str(it.get("label","")).strip()
                value = str(it.get("value","")).strip()
                if not (label and value): 
                    continue
                url = self._build_url(label, value)
                triples.append((label, value, url))
        else:
            # ط´ظƒظ„ ط§ظ„ظ…ظپط§طھظٹط­ ط§ظ„ظ…ط¨ط§ط´ط±ط© (github/linkedin/website/twitterâ€¦)
            for label in ["Website","GitHub","LinkedIn","Twitter","X","YouTube","Facebook","Instagram"]:
                key = label.lower()
                val = data.get(key)
                if not val:
                    # ط¯ط¹ظ… ط­ط§ظ„ط§طھ ط§ظ„طھط³ظ…ظٹط© ط§ظ„ط´ط§ط¦ط¹ط©
                    if label == "Website":
                        val = data.get("site") or data.get("url")
                    if label in ("Twitter","X"):
                        val = data.get("twitter") or data.get("x")
                if not val:
                    continue
                value = str(val).strip()
                if not value:
                    continue
                url = self._build_url(label, value)
                triples.append((label, value, url))
        return triples

    def _build_url(self, label: str, value: str) -> str:
        """ظٹط¨ظ†ظٹ URL ظ†ظ‡ط§ط¦ظٹ ط¨ط§ط³طھط®ط¯ط§ظ… social.py ط¥ظ† ظˆط¬ط¯طŒ ظˆط¥ظ„ط§ ظ‚ظˆط§ط¹ط¯ ط¨ط³ظٹط·ط©."""
        try:
            # ظ„ظˆ social.py ط¹ظ†ط¯ظ‡ ط¯ظˆط§ظ„ ط¨ظ†ط§ط،طŒ ط¬ط±ظ‘ط¨ظ‡ط§
            if hasattr(social, "build_url"):
                return social.build_url(label, value)
            if hasattr(social, "normalize_url"):
                return social.normalize_url(label, value)
        except Exception:
            pass

        v = value.strip()
        low = label.lower()
        if v.startswith("http://") or v.startswith("https://"):
            return v
        if low == "github":
            return f"https://github.com/{v}"
        if low == "linkedin":
            # ظٹظ‚ط¨ظ„ ط´ط®طµظٹ ط£ظˆ ط´ط±ظƒط©
            if v.startswith("in/") or v.startswith("company/"):
                return f"https://www.linkedin.com/{v}"
            return f"https://www.linkedin.com/in/{v}"
        if low in ("twitter","x"):
            return f"https://twitter.com/{v.lstrip('@')}"
        if low == "website":
            return ("https://" + v) if not v.startswith(("http://","https://")) else v
        return v  # fallback

    def render(self, c, frame: Frame, data: Dict[str, Any], ctx: RenderContext) -> float:
        title = (data.get("title") or t("social_links", ctx.get("ui_lang") or UI_LANG))
        triples = self._normalize(data)  # [(label, value, url)]
        if not triples:
            return frame.y

        y = frame.y - LEFT_SEC_TITLE_TOP_GAP
        y = draw_heading_with_icon(
            c=c, x=frame.x, y=y, title=title, icon=get_section_icon("social"),
            font="Helvetica-Bold", size=LEFT_SEC_HEADING_SIZE, color=HEADING_COLOR,
            underline_w=frame.w, rule_color=LEFT_SEC_RULE_COLOR, rule_width=LEFT_SEC_RULE_WIDTH,
            gap_below=LEFT_SEC_TITLE_BOTTOM_GAP / 2,
        )
        y -= LEFT_SEC_RULE_TO_LIST_GAP

        c.setFont("Helvetica", LEFT_TEXT_SIZE)
        c.setFillColor(colors.black)

        for (label, value, url) in triples:
            # ط£ظٹظ‚ظˆظ†ط© ط¥ظ† ظˆط¬ط¯طھ
            icon = ICON_PATHS.get(label.lower()) or ICON_PATHS.get(label)
            text = f"{label}: {value}"

            # ط§ط±ط³ظ… ط§ظ„ظ†طµ
            c.drawString(frame.x, y, text)

            # ظ„ظˆ ظپظٹ URLطŒ ط§ط¹ظ…ظ„ linkURL ط¹ظ„ظ‰ ط¬ط²ط، ط§ظ„ظ‚ظٹظ…ط©
            if url:
                # ط­ط³ط§ط¨ ط¹ط±ط¶ "label: " ط¹ط´ط§ظ† ظ†ط±ط¨ط· ظ…ظ† ط¨ط¹ط¯ظ‡
                prefix = f"{label}: "
                fn = "Helvetica"
                fs = LEFT_TEXT_SIZE
                px = pdfmetrics.stringWidth(prefix, fn, fs)
                tw = pdfmetrics.stringWidth(value, fn, fs)
                asc = pdfmetrics.getAscent(fn)/1000.0 * fs
                dsc = abs(pdfmetrics.getDescent(fn))/1000.0 * fs
                link_rect = (frame.x + px, y - dsc, frame.x + px + tw, y + asc * 0.2)
                try:
                    c.linkURL(url, link_rect, relative=0, thickness=0)
                except Exception:
                    pass

            y -= LEFT_LINE_GAP

        return y

register(SocialLinksBlock())

