"""Central place for abbreviations / terms used in pyplotters.

Keep legends stable and human friendly.

Note: currently used by `bestof_plotter.py` and `trajectory_aggregator.py`.
"""

from __future__ import annotations

import re

# Behavior-policy / group-value names.
# NOTE: keys here MUST match the raw token values found in run-id / cg@ data
# on disk (e.g. bp@ps -> "ps") -- the data itself still says "ps", only the
# *display* value is written as "Beta-Binomial Thompson Sampling" (see
# DISPLAY_TOKEN_TRANSLATIONS below for the cosmetic "ps" -> "bbts" swap used
# when a raw code falls through to a non-dictionary fallback string).
GROUP_VALUE_TERMS: dict[str, str] = {
    "epsilon": "Epsilon Greedy",
    "ps": "Beta-Binomial Thompson Sampling",
    "ucb": "Upper Confidence Bound",

    "lfe": "Lévy Flight"
}

# Config-group ("cg@...") codes are always the bare "<algo>_<bp>" combination
# (e.g. "ql_epsilon", "mcn_ps") -- variant flags like fv/reset/betabinomial
# are separate overrides, not part of the group code, so they must NOT be
# baked into these keys or lookups will silently miss and fall back to "N/A".
# Keys MUST match the raw "mcn"/"ps" tokens actually present in the data;
# only the values (and the fallback path via DISPLAY_TOKEN_TRANSLATIONS) show
# the friendlier "mc" / "bbts" wording.
CONFIG_GROUP_TERMS: dict[str, str] = {
    "ql_epsilon": "Epsilon Greedy",
    "ql_ucb": "Upper Confidence Bound",
    "ql_ps": "Beta-Binomial Thompson Sampling",
    "mcn_epsilon": "Epsilon Greedy",
    "mcn_ucb": "Upper Confidence Bound",
    "mcn_ps": "Beta-Binomial Thompson Sampling",
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

# ===========================================================================================
# COSMETIC DISPLAY RELABELING
# ===========================================================================================
# The underlying data (run-id folder names, cg@ tokens, summary.csv) still uses "mcn" for the
# Monte Carlo family and "ps" for the (now beta-binomial-only) Posterior/Thompson Sampling
# policy -- renaming those on disk is out of scope here. What CAN change is how the plotting
# scripts *display* those tokens: wherever a raw code isn't fully resolved through
# GROUP_VALUE_TERMS / CONFIG_GROUP_TERMS above (e.g. a legend falls back to the raw
# "mcn_epsilon"/"mcn_ps" string), run it through `translate_display_tokens` first so people
# see "mc_epsilon" / "mc_bbts" instead. Matching/lookup logic elsewhere must keep using the
# raw "mcn"/"ps" tokens -- only pass text through this function right before it's shown.
DISPLAY_TOKEN_TRANSLATIONS: dict[str, str] = {
    "mcn": "mc",
    "ps": "bbts",
}

# Splits on the delimiters used inside run-id tokens (underscore, dash, '=') while keeping
# the delimiters themselves, so only whole tokens get swapped -- never partial matches
# inside unrelated words like "epsilon", "reset", or "steps".
_TOKEN_SPLIT_RE = re.compile(r"([_\-=])")


def translate_display_tokens(text: str) -> str:
    """Cosmetically relabel raw codes for display (mcn -> mc, ps -> bbts).

    Only affects text about to be shown to a person (legend labels, plot
    titles, override strings). Never apply this to a string still being used
    to look something up (dict keys, run-id parsing, color/linestyle
    matching) -- those must keep matching the real "mcn"/"ps" data on disk.
    """
    if not text:
        return text
    parts = _TOKEN_SPLIT_RE.split(text)
    return "".join(DISPLAY_TOKEN_TRANSLATIONS.get(part, part) for part in parts)


# ===========================================================================================
# ALGORITHM FORM (Monte Carlo vs Q-Learning)
# ===========================================================================================
# A config-group code is "<algo>_<exploration strategy>" (e.g. "mcn_epsilon", "ql_ps") --
# CONFIG_GROUP_TERMS above only names the strategy. This maps the "<algo>" prefix on its own
# to the full name of the underlying algorithm form, so callers can show both together, e.g.
# "Monte Carlo --- EG". Keys match the raw "mcn"/"ql" prefixes on disk.
ALGO_FAMILY_DISPLAY_NAMES: dict[str, str] = {
    "mcn": "Monte Carlo",
    "ql": "Q-Learning",
}

# Short abbreviation for each exploration strategy, used alongside the algorithm form (e.g.
# "Monte Carlo --- EG"). Keys match the raw "<bp>" suffix of a config-group code (the part
# after "<algo>_"). Lévy Flight has no separate strategy suffix, so it isn't listed here --
# it's shown by its full name instead (see `describe_config_group`).
STRATEGY_ABBR: dict[str, str] = {
    "epsilon": "EG",
    "ucb": "UCB",
    "ps": "BBTS",
}


def describe_config_group(config_group: str) -> str:
    """Describe a config-group code as "<algorithm form> — <strategy abbreviation>", e.g.:
        "mcn_epsilon" -> "Monte Carlo — EG"
        "ql_ucb"      -> "Q-Learning — UCB"
        "mcn_ps"      -> "Monte Carlo — BBTS"
        "lf"          -> "Lévy Flight"  (its own algorithm -- no separate form/strategy to
                                          combine, shown by its full name instead)

    Falls back to a cosmetically-relabeled version of the raw code (mcn -> mc, ps -> bbts,
    see `translate_display_tokens`) if the code isn't recognized, instead of "N/A".
    """
    if not config_group:
        return "N/A"

    if config_group not in CONFIG_GROUP_TERMS:
        return translate_display_tokens(config_group)

    prefix, _, suffix = config_group.partition("_")
    family = ALGO_FAMILY_DISPLAY_NAMES.get(prefix)
    abbr = STRATEGY_ABBR.get(suffix)

    if family and abbr:
        return f"{family} — {abbr}"
    # No separate algorithm form/strategy to combine (e.g. Lévy Flight) -- use the full name.
    return CONFIG_GROUP_TERMS[config_group]