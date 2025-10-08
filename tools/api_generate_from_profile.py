#!/usr/bin/env python3
"""
api_generate_from_profile.py
Use your FastAPI endpoint to generate a full resume PDF using your *real* profile JSON.

1) Start your API server:
   uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload

2) Run:
   python api_generate_from_profile.py [profiles/my_profile.json] --layout two-column.layout.json --theme aqua-card

Output:
  resume_full_api.pdf (in current directory)
"""

from __future__ import annotations
import argparse, json, pathlib, sys, requests

API_URL_DEFAULT = "http://127.0.0.1:8000/generate-form-simple"

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("profile", nargs="?", default="profiles/my_profile.json",
                   help="Path to the profile JSON (default: profiles/my_profile.json)")
    p.add_argument("--api", default=API_URL_DEFAULT, help=f"API URL (default: {API_URL_DEFAULT})")
    p.add_argument("--layout", default="two-column.layout.json",
                   help="Layout name to send to API (the file must exist server-side). Default: two-column.layout.json")
    p.add_argument("--theme", default="aqua-card", help="Theme name (default: aqua-card)")
    p.add_argument("--ui-lang", default="en", help="UI language code (default: en)")
    p.add_argument("--rtl", action="store_true", help="Enable RTL mode")
    p.add_argument("--out", default="resume_full_api.pdf", help="Output PDF filename")
    return p.parse_args()

def main() -> None:
    args = parse_args()
    profile_path = pathlib.Path(args.profile)
    if not profile_path.exists():
        raise SystemExit(f"❌ Profile not found: {profile_path}")

    try:
        profile = json.loads(profile_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"❌ Failed to read/parse profile JSON: {e}", file=sys.stderr)
        raise SystemExit(1)

    payload = {
        "theme_name": args.theme,
        "ui_lang": args.ui_lang,
        "rtl_mode": bool(args.rtl),
        "profile": profile,
        "layout_name": args.layout,  # server will resolve this file
    }

    try:
        r = requests.post(args.api, json=payload, timeout=120)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ HTTP request failed: {e}", file=sys.stderr)
        raise SystemExit(1)

    out_path = pathlib.Path(args.out)
    out_path.write_bytes(r.content)
    print(f"✅ PDF saved: {out_path.resolve()}  ({len(r.content):,} bytes)")

if __name__ == "__main__":
    main()
