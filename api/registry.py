from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def _read_json_name(path: Path) -> str | None:
    """
    Attempts to read a "name" field from a JSON file.

    Args:
        path (Path): The path to the JSON file.

    Returns:
        str | None: The name if found and valid, otherwise None.
    """
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        name = data.get("name")
        if isinstance(name, str) and name.strip():
            return name.strip()
    except Exception:
        pass
    return None

def load_theme_names() -> list[str]:
    """
    Loads and returns a list of available theme names.

    Returns:
        list[str]: A sorted list of unique theme names.
    """
    names = []
    for p in (ROOT / "themes").glob("*.theme.json"):
        n = _read_json_name(p) or p.stem.replace(".theme", "")
        names.append(n)
    return sorted(set(names))

def load_layout_names() -> list[str]:
    """
    Loads and returns a list of available layout names.

    Returns:
        list[str]: A sorted list of unique layout names.
    """
    names = []
    for p in (ROOT / "layouts").glob("*.layout.json"):
        n = _read_json_name(p) or p.stem.replace(".layout", "")
        names.append(n)
    return sorted(set(names))

def load_ui_langs() -> list[dict]:
    """
    Loads UI language definitions from config/ui_langs.json, with fallback defaults.

    Returns:
        list[dict]: A list of dictionaries with code, name, and rtl keys.
    """
    cfg = ROOT / "config" / "ui_langs.json"
    if cfg.exists():
        try:
            data = json.loads(cfg.read_text(encoding="utf-8"))
            out = []
            for item in data:
                code = str(item.get("code", "")).strip()
                if not code:
                    continue
                out.append({
                    "code": code,
                    "name": item.get("name", code),
                    "rtl": bool(item.get("rtl", code in {"ar", "fa", "ur", "he"})),
                })
            seen, uniq = set(), []
            for it in out:
                if it["code"] in seen:
                    continue
                seen.add(it["code"])
                uniq.append(it)
            return uniq
        except Exception:
            pass
    return [
        {"code": "ar", "name": "Arabic", "rtl": True},
        {"code": "en", "name": "English", "rtl": False},
        {"code": "de", "name": "German", "rtl": False},
    ]

def make_str_enum(enum_name: str, values: list[str]) -> type[Enum]:
    """
    Creates a string-based Enum class from a list of values.

    Args:
        enum_name (str): The name of the enum.
        values (list[str]): The values to include in the enum.

    Returns:
        type[Enum]: The generated Enum class.
    """
    if not values:
        values = ["__none__"]
    mapping = {v: v for v in values}
    return Enum(enum_name, mapping, type=str)

THEME_NAMES = load_theme_names()
LAYOUT_NAMES = load_layout_names()
UI_LANG_OBJS = load_ui_langs()
UI_LANGS = [x["code"] for x in UI_LANG_OBJS]
RTL_LANGS = {x["code"] for x in UI_LANG_OBJS if x.get("rtl")}

ThemeNameEnum = make_str_enum("ThemeNameEnum", THEME_NAMES)
LayoutNameEnum = make_str_enum("LayoutNameEnum", LAYOUT_NAMES)
UILangEnum = make_str_enum("UILangEnum", UI_LANGS)

DEFAULT_THEME = "default" if "default" in THEME_NAMES else (THEME_NAMES[0] if THEME_NAMES else "default")
DEFAULT_LAYOUT = "single-column" if "single-column" in LAYOUT_NAMES else (LAYOUT_NAMES[0] if LAYOUT_NAMES else "single-column")
DEFAULT_UI = "ar" if "ar" in UI_LANGS else (UI_LANGS[0] if UI_LANGS else "ar")

