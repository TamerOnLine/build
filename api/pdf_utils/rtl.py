"""Unified module for Arabic text shaping (RTL).

This module performs automatic shaping for Arabic text if both
``arabic_reshaper`` and ``python-bidi`` are available. Otherwise,
it gracefully falls back to returning the input text unchanged.
All code and documentation adhere to PEP 8 standards.
"""

import re

ARABIC_RE = re.compile(r"[\u0600-\u06FF]")

try:
    import arabic_reshaper  # type: ignore
    from bidi.algorithm import get_display  # type: ignore

    def rtl(text: str) -> str:
        """Reshape and reorder Arabic text while leaving Latin words intact.

        Args:
            text: Input string possibly containing Arabic and Latin words.

        Returns:
            The reshaped string suitable for proper RTL rendering. Returns an
            empty string for falsy input.
        """
        if not text:
            return ""
        parts = re.split(r"(\s+)", str(text))
        out = []
        for part in parts:
            if ARABIC_RE.search(part):
                out.append(get_display(arabic_reshaper.reshape(part)))
            else:
                out.append(part)
        return "".join(out)

except Exception:

    def rtl(text: str) -> str:
        """Fallback implementation if Arabic shaping libraries are missing.

        Args:
            text: Input string.

        Returns:
            The text unchanged (or an empty string if falsy).
        """
        return text or ""

