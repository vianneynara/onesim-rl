"""JSON I/O helpers."""

from __future__ import annotations

import json
from typing import Optional, Tuple


def load_json_file(path: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    """Load JSON file.

    Returns:
        (ok, data, error_message)

    Notes:
        - *data* is guaranteed to be a dict when ok=True.
    """

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return False, None, f"JSON root is not an object: {type(data).__name__}"
        return True, data, None
    except FileNotFoundError:
        return False, None, "file not found"
    except json.JSONDecodeError as e:
        return False, None, f"JSON decode error at line {e.lineno} col {e.colno}: {e.msg}"
    except OSError as e:
        return False, None, f"I/O error: {e}"

