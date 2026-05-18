"""Path- and filename-related helper utilities.

Kept separate so batch runners and other scripts can reuse the same validation logic.
"""

from __future__ import annotations

import os
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


def normalize_report_base(report_base: str) -> str:
    """Normalize report base path to absolute path.

    Handles both absolute and relative paths:
    - Absolute paths (e.g., 'D:/reports' or '/home/user/reports'): normalized and returned as-is
    - Relative paths (e.g., 'reports/skripsi' or './reports'): resolved from current working directory

    Args:
        report_base: Base report directory path (absolute or relative)

    Returns:
        Absolute normalized path

    Raises:
        ValueError: if report_base is empty or None
    """
    if not report_base:
        raise ValueError("report_base must not be empty")

    # Convert to absolute path
    # os.path.abspath handles both absolute and relative paths correctly:
    # - Absolute paths are normalized but kept as-is
    # - Relative paths are resolved from current working directory
    abs_path = os.path.abspath(report_base)

    # Normalize the path (removes .. and . components, standardizes separators)
    normalized = os.path.normpath(abs_path)

    return normalized

