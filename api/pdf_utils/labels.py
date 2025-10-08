from __future__ import annotations

# Default language fallback
DEFAULT_LANG = "en"

LABELS: dict[str, dict[str, str]] = {
    "en": {
        "personal_info": "Personal Information",
        "key_skills": "Key Skills",
        "languages": "Languages",
        "selected_projects": "Selected Projects",
        "professional_training": "Professional Training",
    },
    "de": {
        "personal_info": "Pers\u00f6nliche Informationen",
        "key_skills": "Technische F\u00e4higkeiten",
        "languages": "Sprachen",
        "selected_projects": "Ausgew\u00e4hlte Projekte",
        "professional_training": "Berufliche Weiterbildung",
    },
    "ar": {
        "personal_info": "\u0627\u0644\u0645\u0639\u0644\u0648\u0645\u0627\u062a \u0627\u0644\u0634\u062e\u0635\u064a\u0629",
        "key_skills": "\u0627\u0644\u0645\u0647\u0627\u0631\u0627\u062a \u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629",
        "languages": "\u0627\u0644\u0644\u063a\u0627\u062a",
        "selected_projects": "\u0623\u0628\u0631\u0632 \u0627\u0644\u0645\u0634\u0627\u0631\u064a\u0639",
        "professional_training": "\u0627\u0644\u062a\u062f\u0631\u064a\u0628 \u0627\u0644\u0645\u0647\u0646\u064a",
    },
}

def t(key: str, lang: str | None = None) -> str:
    """
    Retrieve the localized label for a given key based on the specified language.

    Args:
        key (str): The label key to look up.
        lang (str | None): Optional language code. Defaults to 'en'.

    Returns:
        str: Localized label string, or the key itself if not found.
    """
    lang = (lang or DEFAULT_LANG).lower()
    return LABELS.get(lang, LABELS[DEFAULT_LANG]).get(key, key)

