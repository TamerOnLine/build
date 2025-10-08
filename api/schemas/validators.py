from __future__ import annotations
import json
from pathlib import Path
from jsonschema import validate, Draft202012Validator

# Define paths to schema files
BASE = Path(__file__).resolve().parents[2]  # Project root directory
SCHEMAS = BASE / "schemas"

# Load JSON schemas
_layout_schema = json.loads((SCHEMAS / "layout.schema.json").read_text(encoding="utf-8"))
_theme_schema = json.loads((SCHEMAS / "theme.schema.json").read_text(encoding="utf-8"))

# Create JSON schema validators
_layout_validator = Draft202012Validator(schema=_layout_schema)
_theme_validator = Draft202012Validator(schema=_theme_schema)

def assert_valid_layout(obj: dict) -> None:
    """
    Validate a layout object against the layout JSON schema.

    Args:
        obj (dict): The layout data to validate.

    Raises:
        ValueError: If validation fails, includes detailed error messages.
    """
    errors = sorted(_layout_validator.iter_errors(obj), key=lambda e: e.path)
    if errors:
        msgs = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors]
        raise ValueError("Layout JSON invalid:\n  - " + "\n  - ".join(msgs))

def assert_valid_theme(obj: dict) -> None:
    """
    Validate a theme object against the theme JSON schema.

    Args:
        obj (dict): The theme data to validate.

    Raises:
        ValueError: If validation fails, includes detailed error messages.
    """
    errors = sorted(_theme_validator.iter_errors(obj), key=lambda e: e.path)
    if errors:
        msgs = [f"{'/'.join(map(str, e.path))}: {e.message}" for e in errors]
        raise ValueError("Theme JSON invalid:\n  - " + "\n  - ".join(msgs))

