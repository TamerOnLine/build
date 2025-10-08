#!/usr/bin/env python
"""
Generates the list of block IDs from api/pdf_utils/blocks/*.py.
Outputs JSON array suitable for GitHub Actions matrix.
- Excludes dunder files and __init__.py
- Optionally filters by prefix/suffix via args in the future
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKS_DIR = ROOT / "api" / "pdf_utils" / "blocks"

def discover_blocks():
    items = []
    if BLOCKS_DIR.is_dir():
        for p in sorted(BLOCKS_DIR.glob("*.py")):
            name = p.stem
            if name.startswith("_") or name == "__init__":
                continue
            items.append(name)
    return items or ["header_name", "contact_info"]  # fallback

if __name__ == "__main__":
    blocks = discover_blocks()
    print(json.dumps(blocks))
