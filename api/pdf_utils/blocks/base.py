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
        """ط§ط±ط³ظ… ط¯ط§ط®ظ„ ط§ظ„ط¥ط·ط§ط± ط§ظ„ظ…ظڈط¹ط·ظ‰ ظˆط£ط¹ط¯ y ط§ظ„ط¬ط¯ظٹط¯ط© ط¨ط¹ط¯ ط§ظ„ط±ط³ظ…."""
        ...

