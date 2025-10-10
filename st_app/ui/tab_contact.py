# streamlit/ui/tab_contact.py
from __future__ import annotations
from typing import Any
import copy
import re
import streamlit as st

from st_app.config.ui_defaults import (
    PH_EMAIL, PH_WEBSITE, PH_PHONE, PH_GITHUB, PH_LINKEDIN, PH_LOCATION,
    MAX_EMAIL, MAX_URL, MAX_PHONE, MAX_GH, MAX_LI, MAX_LOC,
)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _s(x: Any) -> str:
    """Normalize None -> '' and strip strings for safe UI usage."""
    return "" if x is None else str(x).strip()


def _normalize_url(u: str) -> str:
    if not u:
        return ""
    u = u.strip()
    if u.startswith(("http://", "https://")):
        return u
    # Treat naked handles/hosts as full URLs
    return f"https://{u}"


def _normalize_phone(p: str) -> str:
    """Keep digits, +, spaces, hyphens, parentheses; collapse spaces."""
    p = re.sub(r"[^\d+\-\s()]", "", p or "")
    return re.sub(r"\s+", " ", p).strip()


def _maybe_warn_email(email: str) -> None:
    if email and not EMAIL_RE.match(email):
        st.caption("⚠️ That email doesn’t look valid.")


def _maybe_warn_url(label: str, url: str) -> None:
    if url and "." not in url:
        st.caption(f"⚠️ {label} looks unusual.")


def render(profile: dict) -> dict:
    st.subheader("Contact Info")
    rev = st.session_state.get("profile_rev", 0)

    contact = dict(profile.get("contact") or {})
    email_init = _s(contact.get("email"))
    phone_init = _s(contact.get("phone"))
    website_init = _s(contact.get("website"))
    gh_init = _s(contact.get("github"))
    li_init = _s(contact.get("linkedin"))
    location_init = _s(contact.get("location"))

    changed = False
    with st.form(key=f"contact_form_{rev}", clear_on_submit=False):
        c1, c2 = st.columns(2)
        with c1:
            email = st.text_input(
                "Email",
                value=email_init,
                key=f"email_{rev}",
                placeholder=f"e.g., {PH_EMAIL}",
                help="Used on the PDF and for contact buttons.",
                max_chars=MAX_EMAIL,
            )
            website = st.text_input(
                "Website",
                value=website_init,
                key=f"website_{rev}",
                placeholder=f"e.g., {PH_WEBSITE}",
                help="Personal site or portfolio.",
                max_chars=MAX_URL,
            )
        with c2:
            phone = st.text_input(
                "Phone",
                value=phone_init,
                key=f"phone_{rev}",
                placeholder=f"e.g., {PH_PHONE}",
                help="Shown on the PDF (optional).",
                max_chars=MAX_PHONE,
            )
            github = st.text_input(
                "GitHub",
                value=gh_init,
                key=f"github_{rev}",
                placeholder=f"e.g., {PH_GITHUB}",
                help="Handle or full URL.",
                max_chars=MAX_GH,
            )
            linkedin = st.text_input(
                "LinkedIn",
                value=li_init,
                key=f"linkedin_{rev}",
                placeholder=f"e.g., {PH_LINKEDIN}",
                help="Handle or full URL.",
                max_chars=MAX_LI,
            )

        location = st.text_input(
            "Location (optional)",
            value=location_init,
            key=f"location_{rev}",
            placeholder=f"e.g., {PH_LOCATION}",
            max_chars=MAX_LOC,
        )

        submitted = st.form_submit_button("Save contact info")

    if submitted:
        # pull current values, normalize
        email = _s(st.session_state.get(f"email_{rev}", email_init))
        phone = _normalize_phone(_s(st.session_state.get(f"phone_{rev}", phone_init)))
        website = _s(st.session_state.get(f"website_{rev}", website_init))
        github = _s(st.session_state.get(f"github_{rev}", gh_init))
        linkedin = _s(st.session_state.get(f"linkedin_{rev}", li_init))
        location = _s(st.session_state.get(f"location_{rev}", location_init))

        # coerce handles to URLs where useful
        if github and "://" not in github and "/" not in github.strip("/"):
            github = f"https://github.com/{github}"
        github = _normalize_url(github) if github else ""

        if linkedin and "://" not in linkedin and "/" not in linkedin.strip("/"):
            linkedin = f"https://www.linkedin.com/in/{linkedin}"
        linkedin = _normalize_url(linkedin) if linkedin else ""

        website = _normalize_url(website) if website else ""

        # gentle validation hints (UI-only)
        _maybe_warn_email(email)
        _maybe_warn_url("Website", website)
        _maybe_warn_url("GitHub", github)
        _maybe_warn_url("LinkedIn", linkedin)

        # detect changes
        changed = any(
            [
                email != email_init,
                phone != phone_init,
                website != website_init,
                github != gh_init,
                linkedin != li_init,
                location != location_init,
            ]
        )

        # --- IMPORTANT ---
        # Convert empty email "" -> None for API (EmailStr | None)
        email_json = email if email.strip() else None

        # write back
        new_profile = copy.deepcopy(profile)
        new_profile.setdefault("contact", {})
        new_profile["contact"].update(
            {
                "email": email_json,
                "phone": phone,
                "website": website,
                "github": github,
                "linkedin": linkedin,
                "location": location,
            }
        )

        if changed:
            st.session_state["profile_rev"] = rev + 1
            st.success("Contact info updated.")
        else:
            st.info("No changes detected.")

        return new_profile

    # if not submitted, just return the incoming profile untouched
    return profile
