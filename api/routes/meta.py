from fastapi import APIRouter

from api.registry import (
    THEME_NAMES,
    LAYOUT_NAMES,
    UI_LANG_OBJS,
    DEFAULT_THEME,
    DEFAULT_LAYOUT,
    DEFAULT_UI,
)

router = APIRouter(prefix="/meta", tags=["meta"])

@router.get("/choices")
def get_choices():
    """
    Returns available choices for themes, layouts, and UI languages,
    along with their respective default values.

    Returns:
        dict: A dictionary containing available themes, layouts, UI languages,
              and default values for each category.
    """
    return {
        "themes": THEME_NAMES,
        "layouts": LAYOUT_NAMES,
        "ui_langs": UI_LANG_OBJS,
        "defaults": {
            "theme": DEFAULT_THEME,
            "layout": DEFAULT_LAYOUT,
            "ui_lang": DEFAULT_UI,
        },
    }

