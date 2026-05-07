"""Datetime / timedelta formatting helpers."""

from __future__ import annotations

import datetime as dt


def format_timedelta(td: dt.timedelta) -> str:
    """Format a timedelta as HH:MM:SS."""

    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

