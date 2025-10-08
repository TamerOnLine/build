from __future__ import annotations
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

from .base import Frame, RenderContext
from .registry import register


class HeaderBarBlock:
    """
    A top header bar block displaying the user's name or a general title.

    Attributes:
        BLOCK_ID (str): Identifier for the block used in the registry.

    Expected data keys:
        - title (str): The header title text (default: "My Resume").
        - bg (str): Background color in hex (default: "#E0F7FA").
        - fg (str): Foreground/text color in hex (default: "#004D40").
        - pad_mm (float): Padding below the bar in millimeters (default: 4).
    """

    BLOCK_ID = "header_bar"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        """
        Render the header bar with centered text.

        Args:
            c (Canvas): ReportLab canvas for drawing.
            frame (Frame): Frame containing position and size.
            data (dict): Block-specific data.
            ctx (RenderContext): Rendering context (unused).

        Returns:
            float: Updated y-coordinate after rendering the header bar.
        """
        name = data.get("title", "My Resume")
        bg_color = data.get("bg", "#E0F7FA")
        text_color = data.get("fg", "#004D40")
        pad_mm = float(data.get("pad_mm", 4))

        y = frame.y
        h = 12 * mm

        c.setFillColor(colors.HexColor(bg_color))
        c.rect(frame.x, y - h, frame.w, h, stroke=0, fill=1)

        c.setFillColor(colors.HexColor(text_color))
        c.setFont("Helvetica-Bold", 12)
        text_w = stringWidth(name, "Helvetica-Bold", 12)
        c.drawString(frame.x + (frame.w - text_w) / 2, y - h / 2 - 3, name)

        return y - h - pad_mm * mm


# Register the block in the system registry
register(HeaderBarBlock())

