from reportlab.pdfgen.canvas import Canvas
from .base import Frame, RenderContext
from .registry import register


class ProjectsBlock:
    """
    A block that renders a list of projects in a PDF.

    Attributes:
        BLOCK_ID (str): Identifier for the block used in the registry.
    """
    BLOCK_ID = "projects"

    def render(self, c: Canvas, frame: Frame, data: dict, ctx: RenderContext) -> float:
        """
        Render a list of projects in the provided PDF canvas.

        Args:
            c (Canvas): The ReportLab canvas to draw on.
            frame (Frame): The layout frame with position data.
            data (dict): Dictionary containing an "items" key with project info.
            ctx (RenderContext): Context for rendering (unused in this method).

        Returns:
            float: The updated y-coordinate after rendering the content.
        """
        items = data.get("items") or []
        y = frame.y

        c.setFont("Helvetica-Bold", 12)
        c.drawString(frame.x, y, "Projects")
        y -= 12

        for proj in items:
            title, desc, link = (proj + ["", "", ""])[:3]
            c.setFont("Helvetica-Bold", 10)
            c.drawString(frame.x, y, title)
            y -= 10

            c.setFont("Helvetica", 9)
            c.drawString(frame.x, y, desc)
            y -= 12

        return y


# Register the block in the system registry
register(ProjectsBlock())

