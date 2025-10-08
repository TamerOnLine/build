from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

from reportlab.lib import colors
from reportlab.lib.units import mm

from .themes import DEFAULT_THEME
from . import config as cfg

THEMES_DIR = Path(__file__).resolve().parents[2] / "themes"

Number = Union[int, float]

def _to_hex_color(val: str | Number | tuple) -> colors.Color:
    """
    Convert input into a ReportLab Color instance.

    Args:
        val (str | Number | tuple): Color as hex string, grayscale float, or RGB tuple.

    Returns:
        colors.Color: Converted ReportLab color.
    """
    if isinstance(val, colors.Color):
        return val
    if isinstance(val, (int, float)):
        g = max(0.0, min(1.0, float(val)))
        return colors.Color(g, g, g)
    if isinstance(val, (list, tuple)) and len(val) == 3:
        r, g, b = [float(x) for x in val]
        return colors.Color(r, g, b)
    if isinstance(val, str):
        val = val.strip()
        if val.endswith("%"):
            g = max(0.0, min(1.0, float(val[:-1]) / 100.0))
            return colors.Color(g, g, g)
        return colors.HexColor(val)
    return colors.HexColor("#000000")

def _parse_number_with_mm(val: Any) -> float:
    """
    Convert input to float, supporting millimeter suffix.

    Args:
        val (Any): Input value.

    Returns:
        float: Value converted to points.
    """
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        s = val.strip().lower()
        if s.endswith("mm"):
            num = float(s.replace("mm", "").strip())
            return num * mm
        try:
            return float(s)
        except Exception:
            return 0.0
    return 0.0

def _deep_merge(dst: dict, src: dict) -> dict:
    for k, v in (src or {}).items():
        if isinstance(v, dict) and isinstance(dst.get(k), dict):
            _deep_merge(dst[k], v)
        else:
            dst[k] = v
    return dst

def load_theme(theme_name: Optional[str]) -> dict:
    theme = json.loads(json.dumps(DEFAULT_THEME))
    if not theme_name:
        return theme
    p = THEMES_DIR / f"{theme_name}.theme.json"
    if p.exists():
        try:
            user = json.loads(p.read_text(encoding="utf-8"))
            _deep_merge(theme, user)
        except Exception as e:
            print(f"[WARN] Failed to parse theme '{theme_name}': {e}")
    else:
        print(f"[WARN] Theme '{theme_name}' not found at {p}")
    return theme

COLOR_KEYS = {
    "LEFT_BG", "LEFT_BORDER", "HEADING_COLOR", "SUBHEAD_COLOR",
    "MUTED", "RULE_COLOR", "EDU_TITLE_COLOR",
    "LEFT_SEC_RULE_COLOR", "RIGHT_SEC_RULE_COLOR",
}

PT_KEYS = {
    "HEADING_SIZE", "TEXT_SIZE", "NAME_SIZE",
    "LEFT_TEXT_SIZE", "LEFT_SEC_HEADING_SIZE", "LEFT_SEC_TEXT_SIZE",
    "RIGHT_SEC_HEADING_SIZE", "RIGHT_SEC_TEXT_SIZE",
    "BODY_LEADING", "LEADING_BODY", "LEADING_BODY_RTL",
    "GAP_AFTER_HEADING", "GAP_BETWEEN_PARAS", "GAP_BETWEEN_SECTIONS",
    "RIGHT_SEC_RULE_WIDTH", "RIGHT_SEC_RULE_TO_TEXT_GAP",
    "RIGHT_SEC_LINE_GAP", "RIGHT_SEC_SECTION_GAP", "RIGHT_SEC_PARA_GAP",
    "PROJECT_TITLE_SIZE", "PROJECT_TITLE_GAP_BELOW", "PROJECT_DESC_LEADING",
    "PROJECT_DESC_PARA_GAP", "PROJECT_LINK_TEXT_SIZE", "PROJECT_LINK_GAP_ABOVE",
    "PROJECT_BLOCK_GAP", "EDU_TEXT_LEADING", "EDU_BLOCK_TITLE_GAP_BELOW",
    "EDU_BLOCK_GAP", "CARD_RADIUS",
    "LEFT_SEC_TITLE_TOP_GAP", "LEFT_SEC_TITLE_BOTTOM_GAP",
    "LEFT_SEC_RULE_WIDTH", "LEFT_SEC_RULE_TO_LIST_GAP",
    "LEFT_SEC_LINE_GAP", "LEFT_SEC_BULLET_RADIUS",
    "LEFT_SEC_BULLET_X_OFFSET", "LEFT_SEC_TEXT_X_OFFSET",
    "LEFT_SEC_SECTION_GAP", "LEFT_AFTER_CONTACT_GAP",
}

MM_KEYS = {"NAME_GAP", "CARD_PAD", "ICON_SIZE"}

STRING_KEYS = {"LEFT_TEXT_FONT", "LEFT_TEXT_FONT_BOLD", "LINKEDIN_REDIRECT_URL", "UI_LANG"}

BOOL_KEYS = {"LEFT_TEXT_IS_BOLD", "USE_LINKEDIN_REDIRECT", "USE_MOBILE_LINKEDIN"}

FONT_KEYS = {"AR_FONT", "LATIN_FONT", "LATIN_BOLD_FONT"}

def _apply_style_map(style: Dict[str, Any]) -> None:
    for key, val in (style or {}).items():
        try:
            if key in COLOR_KEYS:
                setattr(cfg, key, _to_hex_color(val))
            elif key in MM_KEYS:
                setattr(cfg, key, _parse_number_with_mm(val))
            elif key in PT_KEYS:
                setattr(cfg, key, float(val))
            elif key in STRING_KEYS:
                setattr(cfg, key, str(val))
            elif key in BOOL_KEYS:
                setattr(cfg, key, bool(val))
            elif key in FONT_KEYS:
                setattr(cfg, key, str(val))
        except Exception as e:
            print(f"[WARN] Failed to apply style key {key}={val!r}: {e}")

def _apply_legacy_sections(theme: dict) -> None:
    for k, v in (theme.get("colors") or {}).items():
        if k.lower() in {"heading", "heading_color"}:
            cfg.HEADING_COLOR = _to_hex_color(v)
        elif k.lower() in {"subhead", "subhead_color"}:
            cfg.SUBHEAD_COLOR = _to_hex_color(v)
        elif k.lower() in {"text", "muted", "body"}:
            cfg.MUTED = _to_hex_color(v)
        elif k.lower() in {"rule", "rule_color"}:
            cfg.RULE_COLOR = _to_hex_color(v)
        elif k.lower() in {"left_bg", "panel_bg"}:
            cfg.LEFT_BG = _to_hex_color(v)
        elif k.lower() in {"left_border", "panel_border"}:
            cfg.LEFT_BORDER = _to_hex_color(v)

    for k, v in (theme.get("sizes") or {}).items():
        name = k.upper()
        try:
            setattr(cfg, name, float(v))
        except Exception:
            pass

    for k, v in (theme.get("spacing") or {}).items():
        name = k.upper()
        try:
            setattr(cfg, name, float(v))
        except Exception:
            pass

    for k, v in (theme.get("fonts") or {}).items():
        name = k.upper()
        try:
            setattr(cfg, name, str(v))
        except Exception:
            pass

def apply_theme_to_config(theme: dict) -> None:
    """
    Apply theme settings to the global configuration module.

    Args:
        theme (dict): Theme dictionary to apply.
    """
    _apply_legacy_sections(theme)
    style = theme.get("style") or {}
    _apply_style_map(style)

def load_and_apply(theme_name: Optional[str]) -> dict:
    """
    Load a theme by name and apply it to the global config.

    Args:
        theme_name (Optional[str]): Theme name to load.

    Returns:
        dict: Loaded theme dictionary.
    """
    theme = load_theme(theme_name)
    apply_theme_to_config(theme)
    return theme

