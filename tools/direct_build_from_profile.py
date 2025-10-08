#!/usr/bin/env python3
"""
direct_build_from_profile.py
Build a full resume PDF directly from your *real* profile JSON inside the project.

Usage:
  python direct_build_from_profile.py [profiles/my_profile.json] [--layout layouts/two-column.layout.json] [--theme aqua-card]

Notes:
  - Run this from your project root (where `layouts/`, `themes/`, `profiles/` live).
  - Saves the PDF to out/resume_full.pdf
"""

from __future__ import annotations
from pathlib import Path
import argparse, json, sys

from api.pdf_utils.fonts import register_all_fonts
from api.pdf_utils.builder import build_resume_pdf

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("profile", nargs="?", default="profiles/my_profile.json",
                   help="Path to the profile JSON (default: profiles/my_profile.json)")
    p.add_argument("--layout", default="layouts/two-column.layout.json",
                   help="Path to a layout JSON (default: layouts/two-column.layout.json)")
    p.add_argument("--theme", default="aqua-card",
                   help="Theme name (default: aqua-card)")
    p.add_argument("--ui-lang", default="en", help="UI language code (default: en)")
    p.add_argument("--rtl", action="store_true", help="Enable RTL mode (for Arabic-only content)")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    root = Path(__file__).resolve().parent

    profile_path = (root / args.profile).resolve()
    layout_path  = (root / args.layout).resolve()

    if not profile_path.exists():
        raise SystemExit(f"❌ Profile not found: {profile_path}")
    if not layout_path.exists():
        raise SystemExit(f"❌ Layout not found: {layout_path}")

    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed to read/parse profile JSON: {e}", file=sys.stderr)
        raise SystemExit(1)

    try:
        layout = json.loads(layout_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed to read/parse layout JSON: {e}", file=sys.stderr)
        raise SystemExit(1)

    # Register fonts
    register_all_fonts()

    data = {
        "theme_name": args.theme,
        "ui_lang": args.ui_lang,
        "rtl_mode": bool(args.rtl),
        "profile": profile,
        "layout_inline": layout,
    }

    pdf_bytes = build_resume_pdf(data=data)

    out_dir = root / "out"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "resume_full.pdf"
    out_path.write_bytes(pdf_bytes)
    print(f"✅ PDF generated: {out_path}  ({len(pdf_bytes):,} bytes)")

if __name__ == "__main__":
    main()
