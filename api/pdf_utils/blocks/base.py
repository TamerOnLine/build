from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, TypedDict, Any

@dataclass
class Frame:
    x: float
    y: float
    w: float

class RenderContext(TypedDict, total=False):
    rtl_mode: bool
    ui_lang: str

class Block(Protocol):
    BLOCK_ID: str
    def render(self, c, frame: Frame, data: dict[str, Any], ctx: RenderContext) -> float:
        """ارسم داخل الإطار المُعطى وأعد y الجديدة بعد الرسم."""
        ...


