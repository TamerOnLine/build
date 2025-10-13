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
from .. import social  # نستخدم أدوات التنظيف/البناء من social.py لو متاحة
from .base import Frame, RenderContext
from .registry import register

class SocialLinksBlock:
    """
    تعرض روابط اجتماعية بصيغة مرتبة مع أيقونات + روابط قابلة للنقر.
    data تدعم شكلين:
      A) {"items": [{"label":"GitHub","value":"TamerOnLine"}, {"label":"LinkedIn","value":"tameronline"}, ...]}
      B) {"github":"TamerOnLine","linkedin":"tameronline","website":"https://..."}  (سيُحوَّل داخليًا إلى items)
    يمكن تمرير title اختياريًا.
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
            # شكل المفاتيح المباشرة (github/linkedin/website/twitter…)
            for label in ["Website","GitHub","LinkedIn","Twitter","X","YouTube","Facebook","Instagram"]:
                key = label.lower()
                val = data.get(key)
                if not val:
                    # دعم حالات التسمية الشائعة
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
        """يبني URL نهائي باستخدام social.py إن وجد، وإلا قواعد بسيطة."""
        try:
            # لو social.py عنده دوال بناء، جرّبها
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
            # يقبل شخصي أو شركة
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
            # أيقونة إن وجدت
            icon = ICON_PATHS.get(label.lower()) or ICON_PATHS.get(label)
            text = f"{label}: {value}"

            # ارسم النص
            c.drawString(frame.x, y, text)

            # لو في URL، اعمل linkURL على جزء القيمة
            if url:
                # حساب عرض "label: " عشان نربط من بعده
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


