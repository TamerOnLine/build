# api/pdf_utils/fonts.py
"""
Dynamic Font Loader for ReportLab
Automatically scans /assets for .ttf fonts,
normalizes their names, and registers them dynamically.
"""

import os, re
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.lib.fonts import addMapping

BASE_DIR = os.path.dirname(__file__)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
REGISTERED = set()

# Regex to normalize names like NotoNaskhArabic-Regular â†’ NotoNaskhArabic
STYLE_SUFFIX = re.compile(
    r"[-_](Regular|Bold|Medium|SemiBold|Semi-Bold|ExtraBold|Light|Black|Book|Roman)$",
    flags=re.IGNORECASE,
)

def _normalize_family(name: str) -> str:
    """Return base family name without style suffix."""
    return STYLE_SUFFIX.sub("", name)

def _scan_font_files():
    """Scan assets/ for .ttf and return {family: {'regular': path, 'bold': path}}"""
    families = {}
    for file in os.listdir(ASSETS_DIR):
        if not file.lower().endswith(".ttf"):
            continue
        name = os.path.splitext(file)[0]
        family = _normalize_family(name)
        path = os.path.join(ASSETS_DIR, file)
        fam = families.setdefault(family, {"regular": None, "bold": None})
        lower = name.lower()
        if "bold" in lower or "black" in lower or "semibold" in lower:
            fam["bold"] = path
        else:
            fam["regular"] = path
    return families

def _register_font_family(name: str, paths: dict):
    """Register one family (regular & bold)"""
    try:
        if paths.get("regular"):
            pdfmetrics.registerFont(TTFont(name, paths["regular"]))
            REGISTERED.add(name)
        if paths.get("bold"):
            pdfmetrics.registerFont(TTFont(name + "-Bold", paths["bold"]))
            REGISTERED.add(name + "-Bold")

        # Mapping between normal and bold
        addMapping(name, 0, 0, name)
        if name + "-Bold" in REGISTERED:
            addMapping(name, 0, 1, name + "-Bold")

        print(f"✅ Registered: {name}")
    except Exception as e:
        print(f"Failed to register {name}: {e}")

def register_all_fonts():
    """Register all fonts dynamically"""
    if not os.path.exists(ASSETS_DIR):
        print(f"Font folder not found: {ASSETS_DIR}")
        return
    for family, paths in _scan_font_files().items():
        _register_font_family(family, paths)

    # Unicode fallbacks
    for cid_font in ["HeiseiMin-W3", "STSong-Light", "HYSMyeongJo-Medium"]:
        try:
            pdfmetrics.registerFont(UnicodeCIDFont(cid_font))
        except Exception:
            pass

# Run at import
register_all_fonts()

def ensure_font(font: str):
    """Ensure font is registered before use"""
    if font not in REGISTERED:
        register_all_fonts()

def rtl(text: str) -> str:
    """Placeholder for future Arabic shaping."""
    return text or ""

from reportlab.pdfbase import pdfmetrics

print("ًRegistered font names:")
for f in pdfmetrics.getRegisteredFontNames():
    print("   -", f)

