from __future__ import annotations

import re
from typing import Any

import streamlit as st

from st_app.config.ui_defaults import (
    PH_EMAIL,
    PH_WEBSITE,
    PH_PHONE,
    PH_GITHUB,
    PH_LINKEDIN,
    PH_LOCATION,
    MAX_EMAIL,
    MAX_URL,
    MAX_PHONE,
    MAX_GH,
    MAX_LI,
    MAX_LOC,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def _s(x: Any) -> str:
    """
    Normalize None to an empty string and strip whitespace from strings.

    Args:
        x (Any): The input value to normalize.

    Returns:
        str: A stripped string or empty string if input is None.
    """
    return "" if x is None else str(x).strip()

def _normalize_url(u: str) -> str:
    """
    Normalize a URL to ensure it starts with http or https.

    Args:
        u (str): The input URL.

    Returns:
        str: A properly formatted URL.
    """
    u = (u or "").strip()
    if not u:
        return ""
    return u if u.startswith(("http://", "https://")) else f"https://{u}"

def _normalize_phone(p: str) -> str:
    """
    Normalize a phone number by removing unwanted characters and collapsing spaces.

    Args:
        p (str): The input phone number.

    Returns:
        str: A cleaned phone number string.
    """
    p = re.sub(r"[^\d+\-\s()]", "", p or "")
    return re.sub(r"\s+", " ", p).strip()

def render(profile: dict) -> dict:
    """
    Render the 'Contact Info' tab in a Streamlit app.

    Args:
        profile (dict): The current profile dictionary.

    Returns:
        dict: The updated profile dictionary with contact information.
    """
    st.subheader("Contact Info")

    contact = dict(profile.get("contact") or {})

    email = st.text_input(
        "Email",
        value=_s(contact.get("email")),
        placeholder=PH_EMAIL,
        max_chars=MAX_EMAIL,
        key="contact_email",
    )
    phone = st.text_input(
        "Phone",
        value=_s(contact.get("phone")),
        placeholder=PH_PHONE,
        max_chars=MAX_PHONE,
        key="contact_phone",
    )
    website = st.text_input(
        "Website",
        value=_s(contact.get("website")),
        placeholder=PH_WEBSITE,
        max_chars=MAX_URL,
        key="contact_website",
    )
    github = st.text_input(
        "GitHub",
        value=_s(contact.get("github")),
        placeholder=PH_GITHUB,
        max_chars=MAX_GH,
        key="contact_github",
    )
    linkedin = st.text_input(
        "LinkedIn",
        value=_s(contact.get("linkedin")),
        placeholder=PH_LINKEDIN,
        max_chars=MAX_LI,
        key="contact_linkedin",
    )
    location = st.text_input(
        "Location (optional)",
        value=_s(contact.get("location")),
        placeholder=PH_LOCATION,
        max_chars=MAX_LOC,
        key="contact_location",
    )

    gh = github.strip()
    if gh and "://" not in gh and "/" not in gh.strip("/"):
        gh = f"https://github.com/{gh}"
    gh = _normalize_url(gh) if gh else ""

    li = linkedin.strip()
    if li and "://" not in li and "/" not in li.strip("/"):
        li = f"https://www.linkedin.com/in/{li}"
    li = _normalize_url(li) if li else ""

    wb = _normalize_url(website) if website.strip() else ""
    ph = _normalize_phone(phone)

    email_json = email.strip() or None
    if email_json and not EMAIL_RE.match(email_json):
        st.caption("That email doesn’t look valid.")

    profile["contact"] = {
        "email": email_json,
        "phone": ph or None,
        "website": wb or None,
        "github": gh or None,
        "linkedin": li or None,
        "location": location.strip() or None,
    }

    return profile