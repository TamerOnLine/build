import re

def extract_social_handle(kind: str, value: str):
    """
    Extract and normalize a GitHub or LinkedIn handle from raw input.

    Handles formats such as:
      - Plain handles (e.g., "@username", "username")
      - Full URLs (e.g., "https://github.com/username")
      - Prefixed labels (e.g., "GitHub: username")

    Args:
        kind (str): Platform type; expected values are "GitHub" or "LinkedIn".
        value (str): Raw input string potentially containing a handle or URL.

    Returns:
        tuple[str, str] | None: Normalized handle and full profile URL, or None if invalid.
    """
    v = (value or "").strip()
    if not v:
        return None

    v = re.sub(r'^(https?:\/\/)?(www\.)?', '', v, flags=re.I).strip()
    v = re.sub(r'^\s*(GitHub|LinkedIn)\s*:\s*', '', v, flags=re.I).strip()

    def clean_handle(h: str) -> str:
        h = h.strip()
        h = re.sub(r'^@', '', h)
        return h

    if kind == "GitHub":
        m = re.search(r'^github\.com/([^/?#]+)', v, re.I)
        handle = clean_handle(m.group(1)) if m else clean_handle(v)
        handle = handle.split("/")[0] if "/" in handle else handle
        if handle:
            return handle, f"https://github.com/{handle}"
        return None

    if kind == "LinkedIn":
        m = re.search(r'^linkedin\.com/(?:in|pub)/([^/?#]+)', v, re.I)
        handle = clean_handle(m.group(1)) if m else clean_handle(v)
        handle = handle.split("/")[0] if "/" in handle else handle
        if handle:
            return handle, f"https://www.linkedin.com/in/{handle}"
        return None

    return None

