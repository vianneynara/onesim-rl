"""Path- and filename-related helper utilities.

Kept separate so batch runners and other scripts can reuse the same validation logic.
"""

from __future__ import annotations

import re

# Characters not allowed in Windows filenames/path components
INVALID_CHARS_RE = re.compile(r"[<>:\"/\\|?*]")

WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    "COM1",
    "COM2",
    "COM3",
    "COM4",
    "COM5",
    "COM6",
    "COM7",
    "COM8",
    "COM9",
    "LPT1",
    "LPT2",
    "LPT3",
    "LPT4",
    "LPT5",
    "LPT6",
    "LPT7",
    "LPT8",
    "LPT9",
}


def validate_run_id(run_id: str) -> None:
    """Validate that *run_id* is safe to use as a Windows path component.

    Raises:
        ValueError: if *run_id* is empty or contains Windows-invalid characters.
    """

    if not run_id:
        raise ValueError("run_id must not be empty")

    # Check for illegal characters
    if INVALID_CHARS_RE.search(run_id):
        raise ValueError(
            f"run_id '{run_id}' contains invalid path characters. "
            r"Disallowed characters are: < > : \" / \ | ? *"
        )

    # Check for control chars (ASCII 0-31)
    if any(ord(ch) < 32 for ch in run_id):
        raise ValueError(
            f"run_id '{run_id}' contains control characters, which are not "
            "allowed in Windows filenames."
        )

    # Check for reserved device names (case-insensitive, exact matches only)
    if run_id.upper() in WINDOWS_RESERVED_NAMES:
        raise ValueError(
            f"run_id '{run_id}' is a reserved device name on Windows "
            "(CON, PRN, AUX, NUL, COM1..COM9, LPT1..LPT9). "
            "Please choose a different run_id."
        )

