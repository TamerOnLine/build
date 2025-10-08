# tests/conftest.py
"""
Ensure that the project root is on sys.path for pytest imports.

This allows test files under `tests/` to import modules such as:
    from api.main import app
    from core.schema import ensure_profile_schema
without ImportError issues.
"""

from __future__ import annotations
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
