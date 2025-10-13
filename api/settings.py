# ============================================================
# api/settings.py
# ============================================================
from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import List
import os
import json

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# ============================================================
# 🔧 Default Paths
# ============================================================

def _default_project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _default_profiles_dir() -> Path:
    return Path(
        os.getenv("PROFILES_DIR", str(_default_project_root() / "profiles"))
    ).resolve()


# ============================================================
# ⚙️ Application Settings
# ============================================================

class Settings(BaseSettings):
    # ----- General -----
    app_title: str = "Resume Builder API"
    app_version: str = "1.0.0"
    app_name: str = "Resume API"
    debug: bool = False

    # ----- API -----
    api_prefix: str = "/api"
    api_version: str = "v1"

    # ----- CORS -----
    cors_allow_origins: List[str] = [
        "http://localhost:8501",
        "http://127.0.0.1:8501",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]

    # ----- Paths -----
    project_root: Path = Field(default_factory=_default_project_root)
    profiles_dir: Path = Field(default_factory=_default_profiles_dir)
    public_profiles_mount: str = Field(
        default=os.getenv("PUBLIC_PROFILES_MOUNT", "/profiles")
    )

    # ----- Pydantic v2 Config -----
    model_config = SettingsConfigDict(
        env_prefix="APP_",           # allows APP_DEBUG, APP_API_PREFIX ...
        env_file=".env",             # load from .env if available
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================
    # 🧠 Validators
    # ============================================================

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v):
        """Supports list, JSON, or comma-separated strings."""
        if v is None:
            return []
        if isinstance(v, list):
            return v
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("[") and s.endswith("]"):
                try:
                    data = json.loads(s)
                    if isinstance(data, list):
                        return [str(x).strip() for x in data]
                except Exception:
                    pass
            return [p.strip() for p in s.replace(";", ",").split(",") if p.strip()]
        return v

    @field_validator("cors_allow_methods", "cors_allow_headers", mode="before")
    @classmethod
    def _parse_cors_lists(cls, v):
        """Accepts '*', JSON arrays, or comma-separated values."""
        if v is None:
            return ["*"]
        if isinstance(v, list):
            return v or ["*"]
        if isinstance(v, str):
            s = v.strip()
            if s == "*":
                return ["*"]
            if s.startswith("[") and s.endswith("]"):
                try:
                    data = json.loads(s)
                    if isinstance(data, list) and data:
                        return [str(x).strip() for x in data]
                except Exception:
                    pass
            parts = [p.strip() for p in s.replace(";", ",").split(",") if p.strip()]
            return parts or ["*"]
        return v

    # ============================================================
    # 🧩 Post-Load Normalization
    # ============================================================

    def ensure_dirs_and_normalize(self) -> None:
        """Normalize paths and ensure required directories exist."""
        if not self.public_profiles_mount.startswith("/"):
            self.public_profiles_mount = "/" + self.public_profiles_mount

        self.project_root = Path(self.project_root).resolve()
        self.profiles_dir = Path(self.profiles_dir).resolve()
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # 🧩 Backward-Compatible Aliases
    # ============================================================

    @property
    def API_PREFIX(self) -> str: return self.api_prefix
    @property
    def API_VERSION(self) -> str: return self.api_version
    @property
    def CORS_ALLOW_ORIGINS(self) -> List[str]: return self.cors_allow_origins
    @property
    def CORS_ALLOW_CREDENTIALS(self) -> bool: return self.cors_allow_credentials
    @property
    def CORS_ALLOW_METHODS(self) -> List[str]: return self.cors_allow_methods
    @property
    def CORS_ALLOW_HEADERS(self) -> List[str]: return self.cors_allow_headers
    @property
    def PROJECT_ROOT(self) -> Path: return self.project_root
    @property
    def PROFILES_DIR(self) -> Path: return self.profiles_dir
    @property
    def PUBLIC_PROFILES_MOUNT(self) -> str: return self.public_profiles_mount
    @property
    def APP_TITLE(self) -> str: return self.app_title
    @property
    def APP_VERSION(self) -> str: return self.app_version
    @property
    def DEBUG(self) -> bool: return self.debug


# ============================================================
# 🧩 Singleton Accessor
# ============================================================

@lru_cache
def get_settings() -> Settings:
    s = Settings()
    s.ensure_dirs_and_normalize()
    return s
