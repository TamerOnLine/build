from __future__ import annotations

import base64
import io
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ─────────────────────────────────────────────────────────────
# JSON I/O
# ─────────────────────────────────────────────────────────────

def read_json_file(p: Path) -> Dict[str, Any]:
    """
    Read JSON file as dict. On error or non-dict JSON, return {}.
    """
    try:
        txt = p.read_text(encoding="utf-8")
        obj = json.loads(txt)
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}

def save_profile(path: Path, profile: Dict[str, Any]) -> None:
    """
    Atomically write a profile dict as UTF-8 JSON (pretty, non-ASCII preserved).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(profile or {}, ensure_ascii=False, indent=2)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(path.parent), suffix=".json") as tmp:
        tmp.write(data)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)

def load_profile(path: Path) -> Dict[str, Any]:
    return read_json_file(path)

def list_json_names(folder: Path) -> List[str]:
    """
    List *.json filenames (not paths), excluding hidden/backup files.
    """
    if not folder.exists():
        return []
    out: List[str] = []
    for p in sorted(folder.glob("*.json")):
        name = p.name
        if name.startswith(".") or name.endswith("~"):
            continue
        out.append(name)
    return out

# ─────────────────────────────────────────────────────────────
# Small text/data helpers
# ─────────────────────────────────────────────────────────────

def to_lines(text: Optional[str]) -> List[str]:
    """
    Split text into trimmed, non-empty lines. None -> [].
    Preserves order.
    """
    if not text:
        return []
    return [ln.strip() for ln in text.splitlines() if ln.strip()]

def _coerce_str(x: Any) -> str:
    return "" if x is None else str(x).strip()

def projects_df_to_list(df) -> List[List[str]]:
    """
    Convert a pandas DataFrame with columns (Title, Description, URL) into
    [[title, desc, url], ...], skipping blank rows. Tolerant to missing cols.
    """
    cols = {c.lower(): c for c in getattr(df, "columns", [])}
    c_title = cols.get("title", "Title")
    c_desc  = cols.get("description", "Description")
    c_url   = cols.get("url", "URL")

    rows: List[List[str]] = []
    for _, row in df.iterrows():  # type: ignore[attr-defined]
        title = _coerce_str(row.get(c_title, ""))
        desc  = _coerce_str(row.get(c_desc, ""))
        url   = _coerce_str(row.get(c_url, ""))
        if title or desc or url:
            rows.append([title, desc, url])
    return rows

# ─────────────────────────────────────────────────────────────
# Base64 <-> bytes (supports/produces data URLs)
# ─────────────────────────────────────────────────────────────

_DATA_URL_RE = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<b64>.+)$", re.IGNORECASE)

def encode_photo_to_b64(
    photo_bytes: Optional[bytes],
    photo_mime: Optional[str],
    photo_name: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    Return (photo_b64_or_data_url, mime, name). If bytes are None -> (None, None, None).
    Produces a **data URL** (safer to embed), e.g. 'data:image/png;base64,AAA...'.
    """
    if not photo_bytes:
        return None, None, None
    mime = photo_mime or "image/png"
    name = photo_name or "photo.png"
    b64 = base64.b64encode(photo_bytes).decode("ascii")
    return f"data:{mime};base64,{b64}", mime, name

def decode_photo_from_b64(photo_b64: str) -> bytes:
    """
    Accept raw base64 or a data URL; return decoded bytes.
    Raises ValueError on invalid input.
    """
    if not photo_b64:
        raise ValueError("Empty base64 string")
    s = photo_b64.strip()
    m = _DATA_URL_RE.match(s)
    if m:
        s = m.group("b64")
    try:
        return base64.b64decode(s.encode("ascii"), validate=True)
    except Exception as e:
        # Fallback: try forgiving decode (no validate) if input wasn't strict
        try:
            return base64.b64decode(s.encode("ascii"))
        except Exception:
            raise ValueError(f"Invalid base64 data: {e}") from None
