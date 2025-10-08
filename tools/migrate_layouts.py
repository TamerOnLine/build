from __future__ import annotations
import json, sys
from pathlib import Path

# ظ…ط«ط§ظ„ ظ„ط®ط±ظٹط·ط© ظ‚ط§ظ„ط¨ ظ‚ط¯ظٹظ… -> JSON ط£ظˆظ„ظٹ
LEGACY = {
    "one_column": [
        "header_name", "links_inline", "text_section:summary", "projects", "education"
    ],
    "two_column_left": ["left_panel_bg","avatar_circle","contact_info","key_skills","languages","social_links"],
    "two_column_right": ["header_name","text_section:summary","projects","education"]
}

def emit_one_column(out_path: Path):
    doc = {
        "page": { "size": "A4", "orientation": "portrait",
                  "margin_mm": {"top":22,"right":18,"bottom":18,"left":18}, "gutter_mm": 6 },
        "columns": [ {"id":"main","width":"100%"} ],
        "flow": [ {"column":"main","blocks": LEGACY["one_column"]} ],
        "overrides": {},
        "map_rules": {
            "text_section": {"from":"summary","fn":"text"},
            "key_skills":   {"from":"skills","fn":"list"},
            "languages":    {"from":"languages","fn":"list"},
            "projects":     {"from":"projects","fn":"projects"},
            "education":    {"from":"education","fn":"list"}
        }
    }
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")

def emit_two_column(out_path: Path):
    doc = {
        "page": { "size": "A4", "orientation": "portrait",
                  "margin_mm": {"top":15,"right":12,"bottom":15,"left":12}, "gutter_mm": 8 },
        "columns": [
            {"id":"left","width":"33%","gutter_mm":6},
            {"id":"right","width":"67%"}
        ],
        "flow": [
            {"column":"left","blocks": LEGACY["two_column_left"]},
            {"column":"right","blocks": LEGACY["two_column_right"]}
        ],
        "overrides": {},
        "map_rules": {
            "text_section": {"from":"summary","fn":"text"},
            "key_skills":   {"from":"skills","fn":"list"},
            "languages":    {"from":"languages","fn":"list"},
            "projects":     {"from":"projects","fn":"projects"},
            "education":    {"from":"education","fn":"list"}
        }
    }
    out_path.write_text(json.dumps(doc, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out_path}")

if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]  # project root
    layouts = root / "layouts"
    layouts.mkdir(exist_ok=True)
    emit_one_column(layouts / "one-column.layout.json")
    emit_two_column(layouts / "two-column.layout.json")

