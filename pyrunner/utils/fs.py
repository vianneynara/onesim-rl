"""Filesystem helpers."""

from __future__ import annotations

import os


def safe_int_dirnames(path: str) -> list[int]:
    """Return sorted integer directory names directly under *path*.

    Non-integer directory names and non-directories are ignored.
    """

    if not os.path.isdir(path):
        return []

    episodes: list[int] = []
    try:
        for name in os.listdir(path):
            full = os.path.join(path, name)
            if not os.path.isdir(full):
                continue
            try:
                episodes.append(int(name))
            except ValueError:
                continue
    except OSError:
        return []

    return sorted(set(episodes))

