from reportlab.pdfgen.canvas import Canvas
from ..config import HEADING_COLOR
from .base import Frame, RenderContext
from .registry import register


class HeaderNameBlock:
    """
    A block that renders a header with a name and optional title in a PDF.
    
    Attributes:
        BLOCK_ID (str): Identifier for the block used in the registry.
    """
    BLOCK_ID = "header_name"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        """
        Render the name and title in the provided PDF canvas.

        Args:
            c (Canvas): The ReportLab canvas to draw on.
            frame (Frame): The layout frame with position data.
            data (dict): Dictionary containing "name" and "title" keys.
            ctx (RenderContext): Context for rendering (unused in this method).

        Returns:
            float: The updated y-coordinate after rendering the content.
        """
        name = (data.get("name") or "").strip()
        title = (data.get("title") or "").strip()
        y = frame.y

        if name:
            c.setFont("Helvetica-Bold", 16)
            c.drawString(frame.x, y, name)
            y -= 20

        if title:
            c.setFont("Helvetica", 12)
            c.setFillColor(HEADING_COLOR)
            c.drawString(frame.x, y, title)
            y -= 15

        return y


# Register the block in the system registry
register(HeaderNameBlock())

