from __future__ import annotations
import streamlit as st
from typing import Any

def ok(msg: Any) -> None:
    """Show a green success message."""
    st.success(f"✅ {msg}")

def warn(msg: Any) -> None:
    """Show an amber warning message."""
    st.warning(f"⚠️ {msg}")

def err(msg: Any) -> None:
    """Show a red error message."""
    st.error(f"❌ {msg}")

def info(msg: Any) -> None:
    """Show a blue informational message."""
    st.info(f"ℹ️ {msg}")
