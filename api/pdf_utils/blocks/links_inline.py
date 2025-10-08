from __future__ import annotations
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth

from .base import Frame, RenderContext
from .registry import register


class LinksInlineBlock:
    """
    A block that renders communication links (email, GitHub, LinkedIn, etc.) horizontally.

    Attributes:
        BLOCK_ID (str): Identifier for the block used in the registry.

    Expected data keys:
        - links (list[str]): List of link strings to render.
        - color (str): Text color in hex (default: "#004D40").
    """

    BLOCK_ID = "links_inline"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        """
        Render communication links in a horizontal line.

        Args:
            c (Canvas): ReportLab canvas to draw on.
            frame (Frame): Frame containing layout information.
            data (dict): Block-specific data.
            ctx (RenderContext): Rendering context (unused).

        Returns:
            float: Updated y-coordinate after rendering the links.
        """
        links = data.get("links", [])
        if not links:
            return frame.y

        font = "Helvetica"
        size = 9
        color = data.get("color", "#004D40")

        x = frame.x
        y = frame.y - 10

        c.setFont(font, size)
        c.setFillColor(colors.HexColor(color))

        sep = "  â€¢  "  # bullet separator
        line = sep.join(links)
        c.drawString(x, y, line)

        return y - 10 * mm


# Register the block in the system registry
register(LinksInlineBlock())

