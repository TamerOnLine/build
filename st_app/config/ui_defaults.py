"""
st_app/config/ui_defaults.py
Centralized defaults, placeholders, and limits for the Streamlit UI.
Derived from current UI tabs (Basic, Contact, Education, Headshot, Languages,
Projects, Skills, Summary) and Sidebar.
"""

# ─────────────────────────────────────────────────────────────
# Sidebar defaults
# ─────────────────────────────────────────────────────────────
DEFAULT_API_BASE = "http://127.0.0.1:8000"
UI_LANG_OPTIONS = ["en", "de", "ar"]
DEFAULT_THEME_FALLBACK = "aqua-card.theme.json"   # used if themes list is empty
# Layout list is dynamic from disk; no static default file path here.

# ─────────────────────────────────────────────────────────────
# Basic Info (tab_basic.py)
# ─────────────────────────────────────────────────────────────
MAX_NAME = 120          # same as tab_basic.py
MAX_TITLE = 140         # same as tab_basic.py

PH_FULL_NAME = "e.g., Tamer Hamad Faour"
PH_TITLE = "e.g., Backend Developer · FastAPI & PostgreSQL"

# ─────────────────────────────────────────────────────────────
# Contact Info (tab_contact.py)
# ─────────────────────────────────────────────────────────────
MAX_EMAIL = 120
MAX_URL   = 200
MAX_PHONE = 50
MAX_GH    = 80
MAX_LI    = 120
MAX_LOC   = 120

DEFAULT_DOMAIN = "tamer.dev"   # used for website placeholder
PH_EMAIL    = "you@example.com"
PH_WEBSITE  = f"https://{DEFAULT_DOMAIN}"
PH_PHONE    = "+49 170 123 4567"
PH_GITHUB   = "github.com/TamerOnLine or TamerOnLine"
PH_LINKEDIN = "linkedin.com/in/your-handle or your-handle"
PH_LOCATION = "Berlin, Germany"

# ─────────────────────────────────────────────────────────────
# Education (tab_education.py)
# ─────────────────────────────────────────────────────────────
EDU_COLUMNS = ["Title / Program", "School", "Start", "End", "Details", "URL"]
DATE_HINT = "e.g., 06/2024 or 2024–2025"
EDU_URL_HELP = "Optional: program page or certificate link."

# ─────────────────────────────────────────────────────────────
# Headshot (tab_headshot.py)
# ─────────────────────────────────────────────────────────────
MAX_FILE_MB = 5
MAX_DIM = 4096                # hard cap on largest dimension
DEFAULT_EXPORT = 512          # default square export size (px)
DEFAULT_PHOTO_CIRCLE_MASK = True

# ─────────────────────────────────────────────────────────────
# Languages (tab_languages.py)
# ─────────────────────────────────────────────────────────────
LANGUAGES_TEXTAREA_LABEL = "One per line (e.g., Arabic — Native)"
LANGUAGES_TEXTAREA_HEIGHT = 150

# ─────────────────────────────────────────────────────────────
# Projects (tab_projects.py)
# ─────────────────────────────────────────────────────────────
PROJECT_COLUMNS = ["Title", "Description", "URL"]
PROJECTS_HELP_TITLE = "Project name"
PROJECTS_HELP_DESC  = "One-line summary"
PROJECTS_HELP_URL   = "Optional. We will auto-prefix https:// if missing."

# ─────────────────────────────────────────────────────────────
# Skills (tab_skills.py)
# ─────────────────────────────────────────────────────────────
SKILLS_TEXTAREA_LABEL = "One per line (e.g., Python, FastAPI, Docker...)"
SKILLS_TEXTAREA_HEIGHT = 180

# ─────────────────────────────────────────────────────────────
# Summary (tab_summary.py)
# ─────────────────────────────────────────────────────────────
SUMMARY_TEXTAREA_HEIGHT = 180
PH_SUMMARY = (
    "Example:\\n"
    "Backend Developer experienced with FastAPI, PostgreSQL, and AI-powered tools. "
    "Focused on scalable APIs, clean architecture, and automation."
)

# ─────────────────────────────────────────────────────────────
# Helper accessors (optional)
# ─────────────────────────────────────────────────────────────
def get_placeholders() -> dict:
    """Return a flat mapping of common placeholder strings."""
    return {
        "full_name": PH_FULL_NAME,
        "title": PH_TITLE,
        "email": PH_EMAIL,
        "website": PH_WEBSITE,
        "phone": PH_PHONE,
        "github": PH_GITHUB,
        "linkedin": PH_LINKEDIN,
        "location": PH_LOCATION,
        "summary": PH_SUMMARY,
        "languages_label": LANGUAGES_TEXTAREA_LABEL,
        "skills_label": SKILLS_TEXTAREA_LABEL,
    }
