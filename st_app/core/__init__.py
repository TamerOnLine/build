from __future__ import annotations
import base64
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

def read_json_file(p: Path) -> Dict[str, Any]:
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_profile(path: Path, profile: Dict[str, Any]) -> None:
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

def load_profile(path: Path) -> Dict[str, Any]:
    return read_json_file(path)

def list_json_names(folder: Path) -> List[str]:
    if not folder.exists():
        return []
    return [p.name for p in sorted(folder.glob("*.json"))]

def to_lines(text: str) -> List[str]:
    return [ln.strip() for ln in (text or "").splitlines() if ln.strip()]

def projects_df_to_list(df) -> List[List[str]]:
    rows: List[List[str]] = []
    for _, row in df.iterrows():
        title = str(row.get("Title", "") or "").strip()
        desc  = str(row.get("Description", "") or "").strip()
        url   = str(row.get("URL", "") or "").strip()
        if title or desc or url:
            rows.append([title, desc, url])
    return rows

# Optional helpers for images (kept for compatibility)
def encode_photo_to_b64(photo_bytes: Optional[bytes], photo_mime: Optional[str], photo_name: Optional[str]) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    if not photo_bytes:
        return None, None, None
    return base64.b64encode(photo_bytes).decode("ascii"), (photo_mime or "image/png"), (photo_name or "photo.png")

def decode_photo_from_b64(photo_b64: str) -> bytes:
    return base64.b64decode(photo_b64.encode("ascii"))

