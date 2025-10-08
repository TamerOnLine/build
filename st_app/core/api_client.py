from __future__ import annotations

import base64
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .paths import LAYOUTS_DIR


# ─────────────────────────────────────────────────────────────
# HTTP config
# ─────────────────────────────────────────────────────────────
DEFAULT_BASE = os.getenv("RESUME_API_BASE", "http://127.0.0.1:8000/api")

@dataclass(frozen=True)
class HttpConfig:
    base_url: str = DEFAULT_BASE
    timeout: float = 15.0
    total_retries: int = 2
    backoff_factor: float = 0.25
    status_forcelist: Tuple[int, ...] = (502, 503, 504)
    allowed_methods: Tuple[str, ...] = ("GET", "POST")


def _make_session(cfg: HttpConfig) -> requests.Session:
    s = requests.Session()
    retry = Retry(
        total=cfg.total_retries,
        backoff_factor=cfg.backoff_factor,
        status_forcelist=cfg.status_forcelist,
        allowed_methods=cfg.allowed_methods,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount("http://", adapter)
    s.mount("https://", adapter)
    s.headers.update({"Accept": "application/json"})
    return s


# Global session (simple + performant). If you prefer per-call, instantiate anew.
_HTTP_CFG = HttpConfig()
_SESSION = _make_session(_HTTP_CFG)


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
def _json_or_raise(resp: requests.Response) -> Any:
    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        # Attempt to surface JSON error details if present
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        raise requests.HTTPError(f"{e} :: {detail}") from None
    try:
        return resp.json()
    except Exception:
        raise ValueError("Response did not contain valid JSON")


def _join_url(base: str, path: str) -> str:
    return f"{base.rstrip('/')}/{path.lstrip('/')}"


def normalize_theme_name(name: str) -> str:
    """Drop trailing '.theme.json' if present; API expects bare theme name."""
    return name[:-11] if name.endswith(".theme.json") else name


# ─────────────────────────────────────────────────────────────
# Profiles API
# ─────────────────────────────────────────────────────────────
def list_profiles(base: str = DEFAULT_BASE) -> List[str]:
    url = _join_url(base, "profiles/list")
    r = _SESSION.get(url, timeout=_HTTP_CFG.timeout)
    data = _json_or_raise(r)
    if isinstance(data, list) and all(isinstance(x, str) for x in data):
        return data
    raise TypeError("Unexpected response for profiles/list; expected List[str].")


def load_profile(name: str, base: str = DEFAULT_BASE) -> Dict[str, Any]:
    url = _join_url(base, "profiles/load")
    r = _SESSION.get(url, params={"name": name}, timeout=_HTTP_CFG.timeout)
    data = _json_or_raise(r)
    if isinstance(data, dict):
        return data
    raise TypeError("Unexpected response for profiles/load; expected Dict.")


def save_profile(name: str, profile: Dict[str, Any], base: str = DEFAULT_BASE) -> Dict[str, Any]:
    url = _join_url(base, "profiles/save")
    r = _SESSION.post(url, json={"name": name, "profile": profile}, timeout=max(_HTTP_CFG.timeout, 20))
    data = _json_or_raise(r)
    if isinstance(data, dict):
        return data
    raise TypeError("Unexpected response for profiles/save; expected Dict.")


# ─────────────────────────────────────────────────────────────
# Layout loading (safe)
# ─────────────────────────────────────────────────────────────
def _safe_read_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        txt = path.read_text(encoding="utf-8")
        return json.loads(txt)
    except Exception:
        return None


def choose_layout_inline(selected_name: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Return inline layout JSON if selected; otherwise pick the first '*.layout.json' file,
    falling back to any '*.json' if none found.

    Path traversal is implicitly blocked by joining against LAYOUTS_DIR and not following parents.
    """
    base_dir = Path(LAYOUTS_DIR).resolve()
    if selected_name and selected_name != "(none)":
        candidate = (base_dir / selected_name).resolve()
        if str(candidate).startswith(str(base_dir)) and candidate.is_file():
            return _safe_read_json(candidate)
        return None

    # Prefer *.layout.json, then any *.json
    layout_candidates = sorted(base_dir.glob("*.layout.json")) or sorted(base_dir.glob("*.json"))
    for p in layout_candidates:
        obj = _safe_read_json(p)
        if obj:
            return obj
    return None


# ─────────────────────────────────────────────────────────────
# Generate payload & PDF
# ─────────────────────────────────────────────────────────────
def build_payload(
    theme_name: str,
    ui_lang: str,
    rtl_mode: bool,
    profile: Dict[str, Any],
    layout_inline: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    data: Dict[str, Any] = {
        "theme_name": theme_name,
        "ui_lang": ui_lang or "en",
        "rtl_mode": bool(rtl_mode),
        "profile": profile or {},
    }
    if layout_inline:
        data["layout_inline"] = layout_inline
    return data


_CD_FILENAME_RE = re.compile(r'filename\*?=(?:UTF-8\'\')?"?([^";]+)"?')

def _filename_from_headers(resp: requests.Response, default: str = "resume.pdf") -> str:
    cd = resp.headers.get("Content-Disposition", "")
    m = _CD_FILENAME_RE.search(cd)
    if m:
        try:
            return m.group(1)
        except Exception:
            pass
    return default


def api_generate_pdf(base_url: str, payload: Dict[str, Any], *, stream: bool = False) -> bytes:
    """
    Call POST /generate-form-simple and return PDF bytes.
    If stream=True, downloads in chunks to reduce memory spikes (still returns bytes).
    """
    url = _join_url(base_url, "generate-form-simple")
    if not stream:
        r = _SESSION.post(url, json=payload, timeout=max(_HTTP_CFG.timeout, 60))
        r.raise_for_status()
        # no JSON here; server returns application/pdf
        return r.content

    with _SESSION.post(url, json=payload, timeout=max(_HTTP_CFG.timeout, 60), stream=True) as r:
        r.raise_for_status()
        chunks: List[bytes] = []
        for chunk in r.iter_content(chunk_size=64 * 1024):
            if chunk:
                chunks.append(chunk)
        return b"".join(chunks)


# ─────────────────────────────────────────────────────────────
# Headshot injection
# ─────────────────────────────────────────────────────────────
def inject_headshot_into_layout(
    layout_inline: Optional[Dict[str, Any]],
    photo_bytes: Optional[bytes],
) -> Optional[Dict[str, Any]]:
    """
    If a headshot is present, inject base64 into every 'avatar_circle' block.
    We leave 'photo_bytes' as None so the server can accept either b64 or bytes.
    """
    if not layout_inline or not photo_bytes:
        return layout_inline

    photo_b64 = base64.b64encode(photo_bytes).decode("ascii")
    cloned = json.loads(json.dumps(layout_inline))  # deep clone

    def _walk(node: Any) -> None:
        if isinstance(node, dict):
            if node.get("block_id") == "avatar_circle":
                node.setdefault("data", {})
                node["data"]["photo_b64"] = photo_b64
                node["data"]["photo_bytes"] = None
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for it in node:
                _walk(it)

    _walk(cloned)
    return cloned
