from __future__ import annotations
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib import colors
from reportlab.lib.units import mm

from .base import Frame, RenderContext
from .registry import register


class DecorCurveBlock:
    """
    A decorative curve block rendered at the top of a page or section.

    Attributes:
        BLOCK_ID (str): Identifier for the block used in the registry.

    Expected data keys:
        - height_mm (float): Height of the decorative curve in mm (default: 15).
        - color (str): Hex color for the curve (default: "#E3F2FD").
    """

    BLOCK_ID = "decor_curve"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        """
        Render a decorative curved rectangle.

        Args:
            c (Canvas): The ReportLab canvas to draw on.
            frame (Frame): Frame object with layout dimensions.
            data (dict): Block-specific data.
            ctx (RenderContext): Rendering context (not used here).

        Returns:
            float: Updated y-coordinate for the next block.
        """
        height_mm = float(data.get("height_mm", 15))
        color = data.get("color", "#E3F2FD")
        width = frame.w
        y = frame.y

        c.setFillColor(colors.HexColor(color))
        c.roundRect(
            frame.x,
            y - height_mm * mm,
            width,
            height_mm * mm,
            6 * mm,
            fill=1,
            stroke=0
        )

        return y - height_mm * mm - 2 * mm


# Register the block in the system registry
register(DecorCurveBlock())

