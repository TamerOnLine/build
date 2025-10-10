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

PH_FULL_NAME = "Tamer Hamad Faour"
PH_TITLE = "Backend Developer · FastAPI & PostgreSQL"

# ─────────────────────────────────────────────────────────────
# Contact Info (tab_contact.py)
# ─────────────────────────────────────────────────────────────
MAX_EMAIL = 120
MAX_URL   = 200
MAX_PHONE = 50
MAX_GH    = 80
MAX_LI    = 120
MAX_LOC   = 120

DEFAULT_DOMAIN = "tameronline.com"   # used for website placeholder
PH_EMAIL    = "info@tameronline.com"
PH_WEBSITE  = "https://tameronline.com"
PH_PHONE    = "+49 1607606758"
PH_GITHUB   = "github.com/TamerOnLine or TamerOnLine"
PH_LINKEDIN = "linkedin.com/in/tameronline or TamerOnLine"
PH_LOCATION = "Berlin, Germany"


# ─────────────────────────────────────────────
# Languages (tab_languages.py) — unified like Projects & Education
# ─────────────────────────────────────────────
LANG_COLUMNS = ["Language", "Proficiency"]

# شفافة (placeholder) من بياناتك الفعلية
LANG_HELP_PRIMARY   = "Arabic — Native"
LANG_HELP_SECONDARY = "English — B1 Intermediate"
LANG_HELP_THIRD     = "German — B1 Intermediate"

LANGUAGES_TEXTAREA_LABEL  = "One per line (e.g., Arabic — Native)"
LANGUAGES_TEXTAREA_HEIGHT = 150

LANG_HELP_TEXT = (
    "List each language and your proficiency (e.g., Arabic — Native, English — B1, German — B1)."
)

# ─────────────────────────────────────────────────────────────
# Education (tab_education.py) 
# ─────────────────────────────────────────────────────────────
EDU_COLUMNS = ["Title / Program", "School", "Start", "End", "Details", "URL"]

EDU_HELP_TITLE = "AI (KI) Development – Certificate of Completion"
EDU_HELP_SCHOOL = "MYSTRO GmbH, Wuppertal, Germany"
EDU_HELP_START = "2024-06-18"
EDU_HELP_END = "2024-12-30"
EDU_HELP_DETAILS = (
    "Completed a 1000-hour professional training in Artificial Intelligence, "
    "covering Machine Learning, Deep Learning, and Generative AI. "
    "Certified on 10 January 2025 for demonstrated expertise in modern AI development pipelines."
)
EDU_HELP_URL = "https://sway.cloud.microsoft/BVRyxoeaThCBbIsR"

DATE_HINT = "18.06.2024 or 10.01.2025"
EDU_URL_HELP = "Optional: link to your MYSTRO GmbH AI (KI) Development certificate."



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

PROJECTS_HELP_TITLE = "CVEngine — Dynamic Resume Builder"
PROJECTS_HELP_DESC  = (
    "A Streamlit + FastAPI project for building dynamic resumes with PostgreSQL "
    "and ReportLab PDF generation."
)
PROJECTS_HELP_URL   = "https://github.com/TamerOnLine/CVEngine"

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
