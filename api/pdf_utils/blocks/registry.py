from __future__ import annotations
from typing import Dict, Any

# Global dictionary to store registered blocks
_BLOCKS: Dict[str, Any] = {}

def register(block):
    """
    Register a block in the system using its BLOCK_ID.

    Args:
        block (Any): The block to register. It must have a BLOCK_ID attribute.

    Returns:
        Any: The registered block.

    Raises:
        ValueError: If the block does not define a BLOCK_ID.
    """
    bid = getattr(block, "BLOCK_ID", None)
    if not bid:
        raise ValueError("Block must define BLOCK_ID")

    if bid in _BLOCKS:
        print(f"[Registry] Warning: block '{bid}' already registered, overriding.")
    _BLOCKS[bid] = block
    return block

def get(bid: str):
    """
    Retrieve a block by its ID, supporting compound formats like 'text_section:summary'.

    Args:
        bid (str): The block identifier.

    Returns:
        Any: The retrieved block.

    Raises:
        KeyError: If the block ID is not registered.
    """
    if ":" in bid:
        bid = bid.split(":")[0]
    if bid not in _BLOCKS:
        raise KeyError(f"Block '{bid}' not registered")
    return _BLOCKS[bid]

def list_registered() -> list[str]:
    """
    Return a sorted list of all registered block IDs.

    Returns:
        list[str]: Sorted list of registered block identifiers.
    """
    return sorted(_BLOCKS.keys())

