"""
Module: settings
----------------
Contains configuration settings related to profile storage and public HTTP access.

Environment Variables:
    PROFILES_DIR (str): Path to the profiles directory on the disk.
    PUBLIC_PROFILES_MOUNT (str): Public HTTP path for serving profiles.
"""

import os
from pathlib import Path

# Path to the directory on disk (modifiable via environment variable)
PROFILES_DIR = Path(
    os.getenv(
        "PROFILES_DIR",
        str(Path(__file__).resolve().parent.parent / "profiles")
    )
).resolve()

# Public HTTP mount path (typically static)
PUBLIC_PROFILES_MOUNT = os.getenv("PUBLIC_PROFILES_MOUNT", "/profiles")
