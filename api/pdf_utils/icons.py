from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth

# =========================
# Icon paths and setup
# =========================

ICONS_DIR = Path(__file__).parent / "assets" / "icons"

def icon_path(name: str) -> Path:
    """
    Return the resolved path for a given icon name.

    Args:
        name (str): Icon file name.

    Returns:
        Path: Absolute path to the icon file.
    """
    return (ICONS_DIR / name).resolve()

SECTION_ICON_PATHS: dict[str, Optional[Path]] = {
    "key_skills": icon_path("skills.png"),
    "languages": icon_path("globe.png"),
    "selected_projects": icon_path("laptop.png"),
    "professional_training": icon_path("cap.png"),
}

def get_section_icon(name: str) -> Optional[Path]:
    """
    Retrieve the icon path for a given section name.

    Args:
        name (str): Section identifier.

    Returns:
        Optional[Path]: Path to the section icon if found.
    """
    return SECTION_ICON_PATHS.get(name)

DEFAULT_INFO_ICONS: dict[str, Path] = {
    "address": icon_path("pin.png"),
    "location": icon_path("pin.png"),
    "ort": icon_path("pin.png"),
    "phone": icon_path("phone.png"),
    "telefon": icon_path("phone.png"),
    "mobile": icon_path("phone.png"),
    "email": icon_path("mail.png"),
    "e-mail": icon_path("mail.png"),
    "mail": icon_path("mail.png"),
    "github": icon_path("github.png"),
    "linkedin": icon_path("linkedin.png"),
    "web": icon_path("link.png"),
    "site": icon_path("link.png"),
    "birthdate": icon_path("cake.png"),
    "geburtsdatum": icon_path("cake.png"),
}

ICON_PATHS: dict[str, Path] = {}
ICON_PATHS.update({k: v for k, v in DEFAULT_INFO_ICONS.items() if v and v.is_file()})
ICON_PATHS.update({k: v for k, v in SECTION_ICON_PATHS.items() if v and v.is_file()})

def _text_width(text: str, font_name: str, font_size: int) -> float:
    """
    Calculate the width of a text string for a given font and size.

    Args:
        text (str): The text to measure.
        font_name (str): Name of the font.
        font_size (int): Font size.

    Returns:
        float: Width of the text in points.
    """
    return stringWidth(text, font_name, font_size)

def _maybe_make_link(value: str, label: Optional[str] = None) -> Optional[str]:
    """
    Generate smart hyperlinks (mailto, tel, GitHub, LinkedIn) from string values.

    Args:
        value (str): Input string to convert into a link.
        label (Optional[str]): Label to help determine link type.

    Returns:
        Optional[str]: A hyperlink string or None.
    """
    v = (value or "").strip()

    if v.startswith("http://") or v.startswith("https://"):
        return v
    if "@" in v and " " not in v:
        return f"mailto:{v}"
    if (label or "").lower() in {"telefon", "phone", "mobile"}:
        digits = "".join(ch for ch in v if ch.isdigit() or ch == "+")
        return f"tel:{digits}" if digits else None
    if (label or "").lower() == "github":
        return f"https://github.com/{v}"
    if (label or "").lower() == "linkedin":
        return f"https://www.linkedin.com/in/{v}"

    return None

def draw_heading_with_icon(
    c: canvas.Canvas,
    x: float,
    y: float,
    title: str,
    icon: Optional[Path],
    *,
    font: str = "Helvetica-Bold",
    size: int = 12,
    color=colors.black,
    icon_w: float = 12,
    icon_h: float = 12,
    pad_x: float = 6,
    underline_w: Optional[float] = None,
    rule_color=colors.black,
    rule_width: float = 1.0,
    gap_below: float = 6.0,
    baseline_tweak: float = 9.0,
) -> float:
    """
    Draw a section heading with an optional icon to the left.

    Args:
        c (canvas.Canvas): ReportLab canvas.
        x (float): Starting x-coordinate.
        y (float): Starting y-coordinate.
        title (str): Section title.
        icon (Optional[Path]): Path to the icon file.

    Keyword Args:
        font (str): Font name.
        size (int): Font size.
        color: Font color.
        icon_w (float): Icon width.
        icon_h (float): Icon height.
        pad_x (float): Padding between icon and text.
        underline_w (Optional[float]): Width of underline.
        rule_color: Underline color.
        rule_width (float): Underline stroke width.
        gap_below (float): Gap below text.
        baseline_tweak (float): Vertical adjustment for text baseline.

    Returns:
        float: New y-coordinate after rendering.
    """
    draw_x = x
    if icon and icon.is_file():
        try:
            img = ImageReader(str(icon))
            c.drawImage(img, draw_x, y - icon_h, width=icon_w, height=icon_h, mask="auto")
            draw_x += icon_w + pad_x
        except Exception:
            c.setFont(font, size)
            c.drawString(draw_x, y - baseline_tweak, "â€¢")
            draw_x += _text_width("â€¢ ", font, size)

    c.setFont(font, size)
    c.setFillColor(color)
    c.drawString(draw_x, y - baseline_tweak, title)

    new_y = y - max(icon_h, size) - gap_below
    if underline_w and underline_w > 0:
        c.setStrokeColor(rule_color)
        c.setLineWidth(rule_width)
        c.line(x, new_y, x + underline_w, new_y)
        new_y -= gap_below

    return new_y

def draw_icon_line(
    c: canvas.Canvas,
    x: float,
    y: float,
    text: str,
    *,
    icon: Optional[Path] = None,
    font: str = "Helvetica",
    size: int = 10,
    color=colors.black,
    icon_w: float = 10,
    icon_h: float = 10,
    pad_x: float = 6,
    line_gap: float = 14,
    link: Optional[str] = None,
    max_w: Optional[float] = None,
) -> float:
    """
    Draw a line with optional icon, text, and a hyperlink.

    Args:
        c (canvas.Canvas): ReportLab canvas.
        x (float): Starting x-coordinate.
        y (float): Starting y-coordinate.
        text (str): Text to render.

    Keyword Args:
        icon (Optional[Path]): Path to the icon.
        font (str): Font name.
        size (int): Font size.
        color: Font color.
        icon_w (float): Icon width.
        icon_h (float): Icon height.
        pad_x (float): Padding between icon and text.
        line_gap (float): Vertical gap between lines.
        link (Optional[str]): Optional hyperlink.
        max_w (Optional[float]): Optional max width constraint.

    Returns:
        float: New y-coordinate after rendering.
    """
    draw_x = x
    if icon and icon.is_file():
        try:
            img = ImageReader(str(icon))
            c.drawImage(img, draw_x, y - icon_h + 1, width=icon_w, height=icon_h, mask="auto")
            draw_x += icon_w + pad_x
        except Exception:
            pass

    c.setFont(font, size)
    c.setFillColor(color)
    txt = text or ""
    c.drawString(draw_x, y - (size * 0.8), txt)

    if link:
        tw = _text_width(txt, font, size)
        c.linkURL(link, (draw_x, y - size, draw_x + tw, y + 2), relative=0)

    return y - line_gap

def info_line(
    c: canvas.Canvas,
    x: float,
    y: float,
    label: str,
    value: str,
    *,
    max_w: Optional[float] = None,
    font: str = "Helvetica",
    size: int = 10,
    color=colors.black,
    line_gap: float = 14,
) -> float:
    """
    Draw a personal information line with a possible icon and link.

    Args:
        c (canvas.Canvas): ReportLab canvas.
        x (float): X-coordinate.
        y (float): Y-coordinate.
        label (str): Field label.
        value (str): Field value.

    Keyword Args:
        max_w (Optional[float]): Max width for content.
        font (str): Font name.
        size (int): Font size.
        color: Text color.
        line_gap (float): Vertical spacing after line.

    Returns:
        float: New y-coordinate after rendering.
    """
    lab_lc = (label or "").lower()
    icon = DEFAULT_INFO_ICONS.get(lab_lc)
    link = _maybe_make_link(value, label=lab_lc)
    return draw_icon_line(
        c, x, y, value.strip(),
        icon=icon,
        font=font,
        size=size,
        color=color,
        line_gap=line_gap,
        link=link,
        max_w=max_w
    )

__all__ = [
    "ICONS_DIR",
    "icon_path",
    "get_section_icon",
    "draw_heading_with_icon",
    "draw_icon_line",
    "info_line",
    "SECTION_ICON_PATHS",
    "DEFAULT_INFO_ICONS",
    "ICON_PATHS",
]

