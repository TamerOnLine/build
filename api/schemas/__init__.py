from __future__ import annotations
from typing import Any, Dict, Optional

try:
    # Pydantic v2
    from pydantic import BaseModel, Field
    from pydantic import ConfigDict  # type: ignore[attr-defined]

    class ProfileModel(BaseModel):
        """Profile model allowing any extra fields."""
        model_config = ConfigDict(extra="allow")

    class GenerateFormRequest(BaseModel):
        """Schema for resume generation input."""
        profile: Dict[str, Any] = Field(default_factory=dict)
        theme_name: Optional[str] = None
        layout_name: Optional[str] = None
        ui_lang: Optional[str] = "en"
        rtl_mode: Optional[bool] = False
        filename: Optional[str] = "resume.pdf"

except Exception:
    # Fallback for Pydantic v1
    from pydantic import BaseModel, Field

    class ProfileModel(BaseModel):
        """Profile model allowing any extra fields."""
        class Config:
            extra = "allow"

    class GenerateFormRequest(BaseModel):
        """Schema for resume generation input."""
        profile: Dict[str, Any] = Field(default_factory=dict)
        theme_name: Optional[str] = None
        layout_name: Optional[str] = None
        ui_lang: Optional[str] = "en"
        rtl_mode: Optional[bool] = False
        filename: Optional[str] = "resume.pdf"


__all__ = ["GenerateFormRequest", "ProfileModel"]

