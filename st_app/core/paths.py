from __future__ import annotations
from pathlib import Path

# ─────────────────────────────────────────────────────────────
# Directory structure (auto-created if missing)
# ─────────────────────────────────────────────────────────────
HERE: Path = Path(__file__).resolve().parent.parent  # e.g. streamlit/core → streamlit
ROOT: Path = HERE.parent                             # project root

THEMES_DIR: Path = ROOT / "themes"
LAYOUTS_DIR: Path = ROOT / "layouts"
PROFILES_DIR: Path = ROOT / "profiles"
OUTPUTS_DIR: Path = ROOT / "outputs"

# Ensure all directories exist (including parents)
for d in (THEMES_DIR, LAYOUTS_DIR, PROFILES_DIR, OUTPUTS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ─────────────────────────────────────────────────────────────
# Optional helper
# ─────────────────────────────────────────────────────────────
def subpath(base: Path, *parts: str) -> Path:
    """
    Build a path under one of the known base dirs.
    Example:
        subpath(PROFILES_DIR, "john.json")
    """
    return base.joinpath(*parts)
