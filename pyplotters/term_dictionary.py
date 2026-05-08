"""Central place for abbreviations / terms used in pyplotters.

Keep legends stable and human friendly.

Note: currently used by `persistence_plotter.py` for Best-Of comparison plotting.
"""

from __future__ import annotations

# Behavior-policy / group-value names.
GROUP_VALUE_TERMS: dict[str, str] = {
    "epsilon": "Epsilon Greedy",
    "ts": "Thompson Sampling",
    "ucb": "Upper Confidence Bound",

    "lfe": "Lévy Flight"
}

# Parameter abbreviation -> formal wording.
# (Legends currently use abbreviations, but this dict is kept for future tooltips/annotations.)
PARAM_ABBR_TERMS: dict[str, str] = {
    "ec": "exploration constant",
    "ip": "initial probability",
    "ed": "epsilon decay",
    "me": "minimum epsilon",
    "iv": "initial variance",
}

