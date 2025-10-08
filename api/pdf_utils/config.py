from reportlab.lib import colors
from reportlab.lib.units import mm

"""
PDF Styling Constants for Resume Generator.
Includes typography, layout spacing, color palette, and component sizes.
"""

# -----------------------------
# Typography
# -----------------------------
HEADING_SIZE = 14
TEXT_SIZE = 12
NAME_SIZE = 18
NAME_GAP = 16  # mm

# -----------------------------
# Left Column Font Style
# -----------------------------
LEFT_TEXT_FONT = "Helvetica"
LEFT_TEXT_FONT_BOLD = "Helvetica-Bold"
LEFT_TEXT_IS_BOLD = True

# -----------------------------
# Line Spacing
# -----------------------------
BODY_LEADING = 19
LEADING_BODY = 16
LEADING_BODY_RTL = 20
GAP_AFTER_HEADING = 10
GAP_BETWEEN_PARAS = 10
GAP_BETWEEN_SECTIONS = 12

# -----------------------------
# Color Palette
# -----------------------------
LEFT_BG = colors.HexColor("#F7F8FA")
LEFT_BORDER = colors.HexColor("#E3E6EA")
HEADING_COLOR = colors.blue
SUBHEAD_COLOR = colors.HexColor("#0B7285")
MUTED = colors.HexColor("#6C757D")
RULE_COLOR = colors.HexColor("#D7DBE0")
EDU_TITLE_COLOR = SUBHEAD_COLOR

# -----------------------------
# Card Styling
# -----------------------------
CARD_RADIUS = 6
CARD_PAD = 6 * mm

# -----------------------------
# Icons Row
# -----------------------------
ICON_SIZE = 6 * mm
ICON_PAD_X = 8
ICON_TEXT_DY = -3
ICON_VALIGN = "middle"

# -----------------------------
# Left Inner Section
# -----------------------------
LEFT_TEXT_SIZE = 12
LEFT_LINE_GAP = 16

# -----------------------------
# Left Extra Sections
# -----------------------------
LEFT_SEC_HEADING_SIZE = 14
LEFT_SEC_TEXT_SIZE = 12
LEFT_SEC_TITLE_TOP_GAP = 6
LEFT_SEC_TITLE_BOTTOM_GAP = 6
LEFT_SEC_RULE_COLOR = RULE_COLOR
LEFT_SEC_RULE_WIDTH = 1
LEFT_SEC_RULE_TO_LIST_GAP = 15
LEFT_SEC_LINE_GAP = 18
LEFT_SEC_BULLET_RADIUS = 1.2
LEFT_SEC_BULLET_X_OFFSET = 2.5
LEFT_SEC_TEXT_X_OFFSET = 8
LEFT_SEC_SECTION_GAP = 2
LEFT_AFTER_CONTACT_GAP = 6
LEFT_SEC_TITLE_ALIGN = "left"  # Options: left | center | right

# -----------------------------
# Right Extra Sections
# -----------------------------
RIGHT_SEC_HEADING_SIZE = HEADING_SIZE
RIGHT_SEC_TEXT_SIZE = TEXT_SIZE
RIGHT_SEC_TITLE_TO_RULE_GAP = 10
RIGHT_SEC_RULE_COLOR = RULE_COLOR
RIGHT_SEC_RULE_WIDTH = 0.8
RIGHT_SEC_RULE_TO_TEXT_GAP = 14
RIGHT_SEC_LINE_GAP = 12
RIGHT_SEC_SECTION_GAP = GAP_BETWEEN_SECTIONS
RIGHT_SEC_PARA_GAP = 1

# -----------------------------
# Projects Block
# -----------------------------
PROJECT_TITLE_SIZE = TEXT_SIZE + 1
PROJECT_TITLE_GAP_BELOW = 12
PROJECT_DESC_LEADING = 16
PROJECT_DESC_PARA_GAP = 2
PROJECT_LINK_TEXT_SIZE = TEXT_SIZE - 1
PROJECT_LINK_GAP_ABOVE = -10
PROJECT_BLOCK_GAP = 20

# -----------------------------
# Education Block
# -----------------------------
EDU_TEXT_LEADING = 8
EDU_BLOCK_TITLE_GAP_BELOW = 16
EDU_BLOCK_GAP = 20

# -----------------------------
# LinkedIn Redirect
# -----------------------------
LINKEDIN_REDIRECT_URL = "https://www.linkedin.com/in/"
USE_LINKEDIN_REDIRECT = False
USE_MOBILE_LINKEDIN = False

# -----------------------------
# UI Language Settings
# -----------------------------
# Supported: "en", "de", "ar"
UI_LANG = "en"

