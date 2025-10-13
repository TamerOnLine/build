# st_app/core/layout.py
from __future__ import annotations
from typing import Any, Dict, Optional
import json
from base64 import b64encode

def choose_layout_inline(layout_json: str | None) -> Optional[Dict[str, Any]]:
    """
    يقبل JSON كسلسلة (اختياري) ويُعيد dict. إذا لم يُمرر شيء أو فشل التحويل → يعيد None.
    """
    if not layout_json:
        return None
    try:
        return json.loads(layout_json)
    except Exception:
        # تجاهل الأخطاء وأعد None لتستعمل الـ API الـ layout الافتراضي
        return None

def inject_headshot_into_layout(
    layout: Optional[Dict[str, Any]],
    headshot_bytes: Optional[bytes],
) -> Optional[Dict[str, Any]]:
    """
    إن وُجدت صورة headshot نحقنها في الـ layout بصيغة base64 تحت المفتاح 'headshot'.
    إن لم يوجد layout نُنشئ واحدًا بسيطًا يحتوي على headshot فقط.
    """
    if not headshot_bytes:
        return layout

    b64 = b64encode(headshot_bytes).decode("ascii")
    headshot_block = {
        "inline_base64": f"data:image/png;base64,{b64}"
    }

    if layout is None:
        return {"headshot": headshot_block}

    # لا نعدّل الأصل مباشرة
    new_layout = dict(layout)
    new_layout["headshot"] = headshot_block
    return new_layout
