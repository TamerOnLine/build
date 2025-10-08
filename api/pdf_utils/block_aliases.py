CANONICAL_BLOCKS = {
    # Update this list to reflect actual blocks registered in your system
    "header_name", "projects", "education", "contact_info",
    "languages", "key_skills", "social_links", "avatar_circle",
    "text_section", "left_panel_bg", "decor_curve",
    # Add more as needed...
}

ALIASES = {
    "pprojects": "projects",
    "experiencce": "experience",  # Map to 'experience' if that block exists
    "educatioon": "education",
    "educattion": "education",
    "header_bar": "header_name",  # Map to 'header_name' if 'header_bar' isn't a real block
    # Generic or non-existent blocks mapped to a logical default
    "objective": "text_section",
    "activities": "text_section",
    "rule": "text_section",  # Or create a simple 'Rule' block later
}

def canonicalize(block_id: str) -> str:
    """
    Returns the canonical form of a given block ID using known aliases.

    Args:
        block_id (str): Input block ID.

    Returns:
        str: Canonical block ID.
    """
    bid = block_id.strip()
    return ALIASES.get(bid, bid)

