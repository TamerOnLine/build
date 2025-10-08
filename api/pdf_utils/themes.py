from __future__ import annotations

from reportlab.lib import colors

DEFAULT_THEME = {
    "colors": {
        "heading": "#222222",
        "subhead": "#0A7D55",
        "left_bg": "#F8F9FA",
        "left_border": "#E3E6EA",
        "rule_right": "#D4D7DC",
        "text": "#000000",
    },
    "sizes": {
        "name": 22,
        "heading": 12,
        "text": 10,
        "right_rule_width": 0.6,
    },
    "spacing": {
        "name_gap": 12,
        "gap_after_heading": 8,
    },
    "fonts": {
        "latin": "Helvetica",
        "latin_bold": "Helvetica-Bold",
        "arabic": "NotoNaskhArabic",
    },
}

def to_hex_color(v: str):
    """
    Convert a hexadecimal color string to a ReportLab color.

    Args:
        v (str): Hexadecimal color string (e.g., '#FFFFFF').

    Returns:
        colors.Color: Corresponding ReportLab color object.
    """
    return colors.HexColor(v)

