"""Central place for abbreviations / terms used in pyplotters.

Keep legends stable and human friendly.

Note: currently used by `persistence_plotter.py` for Best-Of comparison plotting.
"""

from __future__ import annotations

# Behavior-policy / group-value names.
GROUP_VALUE_TERMS: dict[str, str] = {
    "epsilon": "Epsilon Greedy",
    "ps": "Posterior Sampling",
    "ucb": "Upper Confidence Bound",

    "lfe": "Lévy Flight"
}

CONFIG_GROUP_TERMS: dict[str, str] = {
    "ql_epsilon": "Epsilon Greedy",
    "ql_ucb": "Upper Confidence Bound",
    "ql_ps_gts": "Gaussian Thompson Sampling",
    "ql_ps_bbts": "Beta-Binomial Thompson Sampling",
    "mcn_fv_epsilon":   "Epsilon Greedy (FV)",
    "mcn_ev_epsilon":  "Epsilon Greedy",
    "mcn_fv_ucb":       "UCB (FV)",
    "mcn_ev_ucb":      "UCB",
    "mcn_fv_ps_gts":    "Gaussian Thompson Sampling (FV)",
    "mcn_ev_ps_gts":   "Gaussian Thompson Sampling",
    "mcn_fv_ps_bbts":   "Beta-Binomial Thompson Sampling (FV)",
    "mcn_ev_ps_bbts":  "Beta-Binomial Thompson Sampling",
    "lf": "Lévy Flight"
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

