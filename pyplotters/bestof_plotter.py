"""Best-of comparison plotter.

This script compares *already processed* runs under `pyplotters/plots/<aof>/...`.
It supports three modes:

1. Best-of mode (--group KEY): selects, for each value of a given group key (e.g. `qlm_bp`),
   the run with the highest `last_episode_cumulative_reward` and overlays their episode series.

2. Compare-all mode (--compareall): compares all available configs without grouping,
   sorted by reward (highest first). Legend shows cfg@N and parameter overrides.

3. Config-group mode (--configgroup KEY): filters runs by config-group key (e.g. cg@ql_epsilon),
   plots all matching runs sorted by reward (descending). Legend shows parameter overrides only.

Assumptions / constraints (by design):
- Must be invoked with `-pid/--parent_id`.
- Requires `pyplotters/plots/<aof>/summary.csv` to exist.
- Requires each referenced `common_data.csv` to exist.
- Run-directory names must be parseable as: <prefix>-<k>@<v>-<k>@<v>-...
  (prefix is ignored). If parsing fails, the script exits with a warning.

Examples:
  # Best-of mode: compare best run per behavior policy
  python -m pyplotters.bestof_plotter -pid ql-c-ms@0-ls@0 --group qlm_bp
  
  # Best-of mode with config filtering
  python -m pyplotters.bestof_plotter -pid ql-c-ms@0-ls@0 --group qlm_bp -c 1-5
  
  # Compare-all mode: plot all configs sorted by reward
  python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --compareall

  # Compare-all with config filtering
  python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --compareall -c 1-5,18-23,29-32
  
  # Config-group mode: compare all runs with cg@ql_epsilon
  python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_epsilon
  
  # Config-group mode with custom title and config filtering
  python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_epsilon -c 1-3,5-7 -t "Epsilon Sensitivity"

Outputs:
  Saves comparison plots into `pyplotters/plots/<aof>/` adjacent to `summary.csv`.
  Filenames end with "(Best-Of Comparison).png", "(Compare-All).png", or 
  "(of group <KEY>).png" depending on mode.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import os
import re
import sys
from dataclasses import dataclass
from typing import Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Allow running this file as a script (python pyrunner/batch_runner.py) while still
# using absolute package imports (pyrunner.*).
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyplotters.term_dictionary import GROUP_VALUE_TERMS

PLOT_RESULTS_DIR = r"pyplotters\\plots"
# PLOT_RESULTS_DIR = r"D:\Developments+\Java\onesim-rl-data\plots"

# BESTOF_CMAP = "viridis"
# BESTOF_CMAP = "magma"
BESTOF_CMAP = "bright"
# BESTOF_CMAP = "deep"
# BESTOF_CMAP = "dark"
# BESTOF_CMAP = "gnuplot2"
# BESTOF_CMAP = "inferno"
# BESTOF_CMAP = "gist_rainbow"

# CURR_CMAP = "Set1"
# CURR_CMAP = "Set3"
# CURR_CMAP = "Spectral"
# CURR_CMAP = "PuOr"
CURR_CMAP = "gist_rainbow"
# CURR_CMAP = "gist_ncar"
# CURR_CMAP = "gist_heat"
# CURR_CMAP = "gist_stern"
# CURR_CMAP = "hsv"
# CURR_CMAP = "cool"
# CURR_CMAP = "winter"

# Constants for episode difference annotations
ANNOTATION_INTERVAL = 50
USE_PERCENTAGE = True

LINE_STYLES = ["-", "--", "-.", ":"]

# Distinct line styles per algorithm family (mcn / ql / lfe), so their lines
# are easy to tell apart even when colors are similar. Anything that doesn't
# match one of these families falls back to DEFAULT_LINESTYLE.
ALGO_FAMILY_LINESTYLES: dict[str, str] = {
    "mcn": "--",   # MCN group -> dashed
    "ql": "-",     # QL group -> solid
    "lfe": ":",    # LFE group -> dotted
}
DEFAULT_LINESTYLE = "-."

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# Keys to ignore in legend labels (algorithm, runs count, config index, config group)
LIST_OF_IGNORED_OVERRIDES = [
    "cfg",  # config index (e.g., cfg@01)
    "cg",   # config group (e.g., cg@ql_epsilon)
    "ql500",  # Q-Learning with 500 runs
    "mcn500",
    "mcn750"
    "lfe500"  # Lévy Flight with 500 runs
    "ql10"
    "lfe10"
]

@dataclass(frozen=True)
class ParsedRunId:
    run_id: str
    tokens: dict[str, str]


def _exit_with_warning(msg: str, code: int = 2) -> None:
    log.warning(msg)
    raise SystemExit(code)


def parse_run_id_strict(run_id: str) -> ParsedRunId:
    """Parse a run-id directory name.

    Expected format: <prefix>-<key>@<value>-<key>@<value>...

    Notes:
    - The first dash-separated component is treated as prefix and ignored.
    - All remaining components *must* contain exactly one '@' and non-empty key/value.
    """
    parts = run_id.split("-")
    if len(parts) < 2:
        _exit_with_warning(
            f"Run-id '{run_id}' does not match expected format: <prefix>-<key>@<value>-..."
        )

    tokens: dict[str, str] = {}
    for raw in parts[1:]:
        if raw.count("@") != 1:
            log.warn(
                f"Run-id '{run_id}' contains invalid token '{raw}'. Expected exactly one '@'."
            )
            log.info(f"Skipping the token {raw}")
            continue
        k, v = raw.split("@")
        if not k or not v:
            _exit_with_warning(
                f"Run-id '{run_id}' contains empty key/value in token '{raw}'."
            )
        if k in tokens:
            _exit_with_warning(
                f"Run-id '{run_id}' contains duplicate key '{k}'. This tool requires unique keys."
            )
        tokens[k] = v

    return ParsedRunId(run_id=run_id, tokens=tokens)


def extract_cfg_index(folder_name: str) -> Optional[int]:
    """Extract cfg index from folder name like 'cfg@05-ql500-...'.

    Returns the integer index (1-based) or None if not found.
    """
    match = re.match(r"cfg@(\d+)", folder_name)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None


def parse_config_indices(config_string: str) -> list[int]:
    """Parse config indices from a string supporting:
    - Single values: "1,2,9"
    - Ranges: "4-6" (expands to 4,5,6)
    - Mixed: "1,2,4-6,9,10-17"

    Returns sorted list of unique integers.
    Raises ValueError if format is invalid.
    """
    configs = set()

    # Split by comma
    parts = config_string.split(",")

    for part in parts:
        part = part.strip()  # Remove whitespace

        if "-" in part:
            # It's a range
            try:
                start_str, end_str = part.split("-", 1)  # Use maxsplit=1 to handle negative numbers
                start = int(start_str.strip())
                end = int(end_str.strip())

                if start > end:
                    raise ValueError(f"Invalid range '{part}', start > end")

                # Add all values in range (inclusive)
                for i in range(start, end + 1):
                    configs.add(i)
            except ValueError as e:
                raise ValueError(f"Invalid range format '{part}': {e}")
        else:
            # It's a single value
            try:
                configs.add(int(part))
            except ValueError:
                raise ValueError(f"Invalid config number '{part}' (must be integer)")

    return sorted(list(configs))


def filter_summary_by_configs(summary_df: pd.DataFrame, config_indices: list[int]) -> pd.DataFrame:
    """Filter summary DataFrame to include only rows matching specified config indices.

    Matches configuration_directory entries starting with 'cfg@N' where N is in config_indices.

    Args:
        summary_df: DataFrame with 'configuration_directory' column
        config_indices: List of integer config indices to include (1-based)

    Returns:
        Filtered DataFrame with only matching rows
    """
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")

    # Track which configs were requested but not found
    requested_indices = set(config_indices)
    found_indices = set()

    # Filter rows by matching cfg@ index
    mask = pd.Series([False] * len(summary_df), index=summary_df.index)
    for idx, row in summary_df.iterrows():
        config_dir = str(row["configuration_directory"])
        cfg_idx = extract_cfg_index(config_dir)

        if cfg_idx is not None and cfg_idx in config_indices:
            mask.iloc[idx] = True
            found_indices.add(cfg_idx)

    filtered_df = summary_df[mask]

    # Warn about missing configs
    missing_indices = requested_indices - found_indices
    if missing_indices:
        for cfg_idx in sorted(missing_indices):
            log.warning(
                f"Requested config cfg@{cfg_idx} not found in summary.csv. Skipping."
            )

    if len(filtered_df) == 0:
        _exit_with_warning(
            f"No runs found matching requested configs: {sorted(config_indices)}"
        )

    log.info(f"Filtered to {len(filtered_df)} runs from configs: {sorted(found_indices)}")
    return filtered_df


def filter_summary_by_configgroup(summary_df: pd.DataFrame, cg_key: str) -> pd.DataFrame:
    """Filter summary DataFrame to include only rows matching a config-group key.

    Matches configuration_directory entries containing 'cg@<cg_key>'.

    Args:
        summary_df: DataFrame with 'configuration_directory' column
        cg_key: The config-group value to filter by (e.g., 'ql_epsilon')

    Returns:
        Filtered DataFrame with only matching rows
    """
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")

    # Filter rows by matching cg@ value
    mask = pd.Series([False] * len(summary_df), index=summary_df.index)
    found_count = 0

    for idx, row in summary_df.iterrows():
        config_dir = str(row["configuration_directory"])
        try:
            pr = parse_run_id_strict(config_dir)
            if "cg" in pr.tokens and pr.tokens["cg"] == cg_key:
                mask.iloc[idx] = True
                found_count += 1
        except SystemExit:
            # Skip runs that can't be parsed
            continue

    filtered_df = summary_df[mask]

    if len(filtered_df) == 0:
        _exit_with_warning(
            f"No runs found with config-group cg@{cg_key}. Available runs must contain 'cg@{cg_key}' token."
        )

    log.info(f"Filtered to {len(filtered_df)} runs with config-group cg@{cg_key}")
    return filtered_df


def detect_algo_family(run_id: str) -> str:
    """Classify a run-id into an algorithm family ('mcn', 'ql', or 'lfe').

    Looks at every dash-separated token in `run_id` (e.g. the prefix, or bare
    tokens like 'ql500'/'mcn750'/'lfe10') and matches it against the known
    family prefixes. Returns "" if no known family is found.
    """
    for part in run_id.split("-"):
        m = re.match(r"^(mcn|ql|lfe)\d*$", part, flags=re.IGNORECASE)
        if m:
            return m.group(1).lower()
    return ""


def get_linestyle_for_run(run_id: str) -> str:
    """Return the linestyle to use for a given run-id, based on its algorithm family."""
    family = detect_algo_family(run_id)
    return ALGO_FAMILY_LINESTYLES.get(family, DEFAULT_LINESTYLE)


# A curated set of bold, maximally-distinct colors (a trimmed version of the
# well-known "20 distinct colors" qualitative palette, with pale/pastel
# entries removed since those wash out in line plots on a white background).
# Deliberately includes true red, green, blue, orange, purple, etc. so
# adjacent lines never end up looking like near-identical hues, which a raw
# hash-to-hue-wheel approach can produce by chance.
# A curated set of bold, maximally-distinct colors (a trimmed version of the
# well-known "20 distinct colors" qualitative palette, with pale/pastel
# entries removed since those wash out in line plots on a white background).
# Used as a FALLBACK for color keys with no fixed assignment below.
QUALITATIVE_PALETTE: list[str] = [
    "#e6194B",  # red
    "#4363d8",  # blue
    "#3cb44b",  # green
    "#f58231",  # orange
    "#911eb4",  # purple
    "#42d4f4",  # cyan
    "#f032e6",  # magenta
    "#9A6324",  # brown
    "#469990",  # teal
    "#d4ac0d",  # gold (deeper than pure yellow, which is hard to see on white)
    "#800000",  # maroon
    "#000075",  # navy
    "#808000",  # olive
    "#a9a9a9",  # grey
]

# Known exploration-strategy ("bp") categories get FIXED, obvious colors
# instead of being left to hashing luck. Hashing guarantees the same key
# always gets the same color, but not that two specific categories that both
# show up on one plot (e.g. "epsilon" and "ps") land on colors that are easy
# to tell apart -- they could both hash near each other (e.g. magenta and
# purple). Hand-picking the handful of categories that actually occur avoids
# that entirely: epsilon is always red, ucb is always blue, ps is always
# green, no matter what else is on the plot.
KNOWN_BP_COLORS: dict[str, str] = {
    "epsilon": "#3cb44b",  # green
    "ucb": "#e6194B",      # red
    "ps": "#4363d8",       # blue
}
# Levy Flight has no "bp" override (its tunable parameter is "la"), so it
# gets its own fixed color the same way.
LEVY_FLIGHT_COLOR = "#f58231"  # orange

# Colors already reserved above are excluded from the generic hashed
# fallback, so they stay uniquely tied to epsilon/ucb/ps/Levy-Flight and never
# get accidentally reused for an unrelated key.
_RESERVED_COLORS = set(KNOWN_BP_COLORS.values()) | {LEVY_FLIGHT_COLOR}
_FALLBACK_PALETTE = [c for c in QUALITATIVE_PALETTE if c not in _RESERVED_COLORS]


def color_for_key(color_key: str) -> str:
    """Map a color key (e.g. "bp=epsilon", "la", or an override string) to a color.

    Known categories (see KNOWN_BP_COLORS / LEVY_FLIGHT_COLOR) get a fixed,
    semantically obvious color every time. Anything else falls back to a
    deterministic hash into the remaining palette -- the SAME key still always
    produces the SAME color, in every plot, regardless of what else is being
    plotted alongside it or which separate run of this script generated it.

    Note: with more distinct fallback color keys on one plot than colors left
    in the fallback palette, some keys will repeat colors (still
    distinguishable by linestyle/legend).
    """
    if color_key.startswith("bp="):
        bp_value = color_key[len("bp="):]
        if bp_value in KNOWN_BP_COLORS:
            return KNOWN_BP_COLORS[bp_value]
    elif color_key == "la":
        return LEVY_FLIGHT_COLOR

    digest = hashlib.md5(color_key.encode("utf-8")).hexdigest()
    idx = int(digest, 16) % len(_FALLBACK_PALETTE)
    return _FALLBACK_PALETTE[idx]


def key_to_abbr(key: str) -> str:
    """Convert an override key to its abbreviation.

    Example: "ucb_ec" -> "ec" (substring after last underscore)
             "ps_iv"  -> "iv"
             "foo"    -> "foo"
    """
    if "_" in key:
        return key.rsplit("_", 1)[-1]
    return key


def build_overrides_str(overrides: dict[str, str]) -> str:
    """Build the 'abbr=value, abbr=value' string for a dict of overrides.

    Sorted by abbreviation for a stable, deterministic string. Used for
    legend labels, and as a color-key fallback (see `build_color_key`).
    """
    items: list[tuple[str, str]] = [(key_to_abbr(k), str(v)) for k, v in overrides.items()]
    items.sort(key=lambda t: t[0])
    return ", ".join([f"{abbr}={val}" for abbr, val in items])


def build_color_key(overrides: dict[str, str]) -> str:
    """Build the key used to determine a line's color.

    If the overrides include a "bp" (behavior policy / exploration strategy)
    parameter -- e.g. bp=epsilon, bp=ucb, bp=ps -- that value ALONE is used
    as the color key. This is what makes e.g. mcn_epsilon and ql_epsilon get
    the same color: they share bp=epsilon even though every other tuned
    hyperparameter differs between the two families' best runs. Linestyle
    (per algorithm family) still distinguishes them.

    If there's no "bp" but there IS an "la" (Levy Flight's alpha parameter),
    the category key is just "la" -- so all Levy Flight lines get the same
    fixed color regardless of the specific alpha value tuned.

    Falls back to the full overrides string (same as `build_overrides_str`)
    when neither is present -- e.g. plain parameter sweeps where matching an
    exact value (like a specific epsilon coefficient) across plots is the
    goal instead.
    """
    for k, v in overrides.items():
        if key_to_abbr(k) == "bp":
            return f"bp={v}"
    for k in overrides:
        if key_to_abbr(k) == "la":
            return "la"
    return build_overrides_str(overrides)


def build_legend_label(group_value: str, overrides: dict[str, str]) -> str:
    """Build legend label in the form: '<group> (abbr=value, abbr=value)'.

    Overrides are sorted by abbreviation for stable legends.
    """
    # Expand group value with formal wording when available.
    group_display = GROUP_VALUE_TERMS.get(group_value, group_value)

    overrides_str = build_overrides_str(overrides)
    return f'{group_display} {"("+overrides_str+")" if overrides_str else ""}'


def best_of_by_group(summary_df: pd.DataFrame, group_key: str, addparams: Union[dict[str, str], None] = None) -> pd.DataFrame:
    """Return DF with the single best run per group value.

    Args:
        summary_df: DataFrame with summary data
        group_key: The key to group runs by (e.g., 'qlm_bp')
        addparams: Optional dict of {key: value} phantom parameters to inject into runs
                   that lack the group_key. If a key already exists in a run, it is skipped
                   with a warning.
    """
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")
    if "last_episode_cumulative_reward" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'last_episode_cumulative_reward'.")

    if addparams is None:
        addparams = {}

    records: list[dict[str, str]] = []
    injections_made = []
    skipped_injections = []

    for run_id in summary_df["configuration_directory"].astype(str).tolist():
        pr = parse_run_id_strict(run_id)
        group_value = None  # Will be set in if/else block or exit

        # Check if group_key exists in tokens
        if group_key not in pr.tokens:
            # Try to inject from addparams
            if group_key in addparams:
                group_value = addparams[group_key]
                injections_made.append((run_id, group_key, group_value))
                log.info(f"Injecting phantom param '{group_key}@{group_value}' into run-id '{run_id}'")
            else:
                _exit_with_warning(
                    f"Run-id '{run_id}' does not contain required group key '{group_key}@...' "
                    f"and no addparam '{group_key}@...' was provided."
                )
        else:
            group_value = pr.tokens[group_key]

        # Check for conflicts: if user tried to add a param that already exists, warn and skip
        for add_key, add_value in addparams.items():
            if add_key in pr.tokens and add_key != group_key:
                existing_value = pr.tokens[add_key]
                skipped_injections.append((run_id, add_key, add_value, existing_value))
                log.warning(
                    f"Run-id '{run_id}' already contains key '{add_key}@{existing_value}'; "
                    f"skipping requested injection '{add_key}@{add_value}'."
                )

        overrides = {k: v for k, v in pr.tokens.items()
                    if k != group_key and k not in LIST_OF_IGNORED_OVERRIDES}
        records.append(
            {
                "configuration_directory": run_id,
                "group_value": group_value,
                "legend_label": build_legend_label(group_value, overrides),
                "overrides_key": build_color_key(overrides),
            }
        )

    # Log summary of injections
    if injections_made:
        log.info(f"Phantom parameter injections: {len(injections_made)} run(s) modified")
    if skipped_injections:
        log.info(f"Skipped conflicting injections: {len(skipped_injections)} param(s) already exist")

    parsed_df = pd.DataFrame(records)
    merged = summary_df.merge(parsed_df, on="configuration_directory", how="left")

    merged = merged.copy()
    merged["last_episode_cumulative_reward"] = pd.to_numeric(merged["last_episode_cumulative_reward"], errors="coerce")
    if merged["last_episode_cumulative_reward"].isna().any():
        _exit_with_warning("summary.csv contains non-numeric last_episode_cumulative_reward values; aborting.")

    merged = merged.sort_values(
        by=["group_value", "last_episode_cumulative_reward", "configuration_directory"],
        ascending=[True, False, True],
        kind="mergesort",
    )
    return merged.groupby("group_value", as_index=False).head(1)


def _sanitize_filename(name: str) -> str:
    illegal = '<>:"/\\|?*'
    for ch in illegal:
        name = name.replace(ch, "-")
    return name.strip().rstrip(".")


def print_final_summary(
    entries: list[tuple[str, Optional[int], str, float]],
    heading: str,
) -> list[int]:
    """Print a clean final summary block: one line per entry (name + cfg@N +
    reward), followed by a single flat list of the cfg@ numbers involved.

    Args:
        entries: list of (label, cfg_idx, run_id, reward)
        heading: title line printed above the table

    Returns:
        Sorted, de-duplicated list of cfg indices printed at the bottom.
    """
    print()
    print("=" * LINE_LENGTH)
    print(heading)
    print("=" * LINE_LENGTH)

    config_numbers: list[int] = []
    for label, cfg_idx, run_id, reward in entries:
        cfg_str = f"cfg@{cfg_idx}" if cfg_idx is not None else "cfg@?"
        reward_str = f"{reward:.2f}" if reward is not None and not pd.isna(reward) else "N/A"
        print(f"  {label:<45s} {cfg_str:<10s} reward={reward_str}  ({run_id})")
        if cfg_idx is not None:
            config_numbers.append(cfg_idx)

    config_numbers = sorted(set(config_numbers))

    print("-" * LINE_LENGTH)
    print(f"Config numbers: {config_numbers}")
    print("=" * LINE_LENGTH)

    return config_numbers


def plot_bestof_by_episode(
    series_by_label: list[tuple[str, pd.DataFrame, str, str]],
    y_key: str,
    title: str,
    xlabel: str,
    ylabel: str,
    out_file: str,
    suptitle: SuptitleFormat = None,
    legend_outside: bool = False,
    legend_side: bool = False,
    cmap: str = None,  # unused now that color is deterministic/hash-based (kept for call-site compatibility)
    annotate_diff: bool = False,
    diff_interval: int = ANNOTATION_INTERVAL,
):
    if not series_by_label:
        _exit_with_warning("No best-of series to plot.")

    plt.figure(figsize=(10, 6))

    max_ep = None
    min_ep = None
    for _, df, _, _ in series_by_label:
        if "episodeNumber" not in df.columns:
            _exit_with_warning("common_data.csv missing required column 'episodeNumber'.")
        max_ep = int(df["episodeNumber"].max()) if max_ep is None else max(max_ep, int(df["episodeNumber"].max()))
        min_ep = int(df["episodeNumber"].min()) if min_ep is None else min(min_ep, int(df["episodeNumber"].min()))

    # Color is keyed by `color_key` (the parameter-override string, e.g.
    # "ec=0.1") and derived via a hash, NOT by position in this plot's list of
    # lines. This is what makes colors match across separate plots/invocations
    # -- e.g. mc epsilon=0.1 and ql epsilon=0.1 get the SAME color even when
    # plotted in different calls to this script with different value sets --
    # while linestyle (set per algorithm family) still tells the lines apart.
    unique_color_keys = sorted({color_key for _, _, _, color_key in series_by_label})
    color_map = {k: color_for_key(k) for k in unique_color_keys}

    for idx, (label, df, run_id, color_key) in enumerate(series_by_label):
        if y_key not in df.columns:
            _exit_with_warning(f"common_data.csv missing required column '{y_key}'.")

        color = color_map[color_key]
        final_line_style = get_linestyle_for_run(run_id)
        sns.lineplot(data=df, x="episodeNumber", y=y_key, label=label, color=color, linestyle=final_line_style)

    # Add difference annotations if enabled
    if annotate_diff:
        ax = plt.gca()

        for idx, (label, df, run_id, color_key) in enumerate(series_by_label):
            color = color_map[color_key]
            # Calculate point-to-point differences
            df_sorted = df.sort_values(by="episodeNumber").reset_index(drop=True)
            y_values = pd.to_numeric(df_sorted[y_key], errors="coerce")
            episode_numbers = df_sorted["episodeNumber"]

            # Iterate through data points, starting from index 1 (skip first point)
            for i in range(1, len(df_sorted)):
                current_episode = episode_numbers.iloc[i]

                # Only annotate at interval boundaries
                if current_episode % diff_interval == 0:
                    current_y = y_values.iloc[i]
                    previous_y = y_values.iloc[i - 1]

                    # Skip if either value is NaN
                    if pd.isna(current_y) or pd.isna(previous_y):
                        continue

                    # Calculate difference
                    if USE_PERCENTAGE:
                        if previous_y != 0:
                            diff = ((current_y - previous_y) / abs(previous_y)) * 100
                            label_text = f"{diff:+.2f}%"
                        else:
                            continue
                    else:
                        diff = current_y - previous_y
                        label_text = f"{diff:+.2f}"

                    # Annotate the point with line's color
                    ax.annotate(label_text,
                               xy=(current_episode, current_y),
                               xytext=(0, 10),
                               textcoords='offset points',
                               ha='center', fontsize=8, color=color)

    if max_ep is not None and min_ep is not None:
        if max_ep <= 20:
            ticks = np.arange(min_ep, max_ep + 1, 1)
        else:
            step = max(1, max_ep // 10)
            start = (min_ep // step) * step
            ticks = np.arange(start, max_ep + 1, step)
        plt.xticks(ticks)
        plt.xlim(left=min_ep, right=max_ep)

    # Construct title with suptitle and subtitle
    if suptitle.title != "":
        fig = plt.gcf()

        fig.suptitle(
            suptitle.title,
            fontweight="bold",
            fontsize=12,
            y=0.99
        )

        plt.title(title, fontweight="bold", fontsize=10)

        extra_lines = max(0, suptitle.newline_gap - 1)

        fig.subplots_adjust(
            top=0.92 - (0.04 * extra_lines)
        )
    else:
        # Single title (backward compatible)
        plt.title(title, fontweight="bold")

    plt.xlabel(xlabel, fontweight="bold")
    plt.ylabel(ylabel, fontweight="bold")
    plt.margins(x=0)

    ax = plt.gca()
    handles, _labels = ax.get_legend_handles_labels()
    if handles:
        if legend_side:
            # Place legend outside the plot, on the right side as a single column
            ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(1.02, 1), ncol=1, borderaxespad=0, prop={"family": "monospace"})
        elif legend_outside:
            # Place legend outside the plot, below it as a single column
            ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0, -0.15), ncol=1, prop={"family": "monospace"})
        else:
            # Place legend inside the plot (default behavior)
            ax.legend(handles=handles, loc="best", prop={"family": "monospace"})

    out_dir = os.path.dirname(out_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()


def run_compareall(all_of: str, suptitle: SuptitleFormat = None, config_indices: Union[list[int], None] = None, annotate_diff: bool = False, legend_outside: bool = False, legend_side: bool = False) -> None:
    """Compare all available configurations (no grouping, no best-of selection).

    Plots all configs with legend labels showing cfg@N and parameter overrides.
    Runs are sorted by last_episode_cumulative_reward (descending) for ordering.

    Args:
        all_of: Parent results directory under pyplotters/plots
        suptitle: Optional custom title for plots
        config_indices: Optional list of config indices to filter by
    """
    out_dir = os.path.join(PLOT_RESULTS_DIR, all_of)
    summary_path = os.path.join(out_dir, "summary.csv")

    if not os.path.exists(out_dir):
        _exit_with_warning(
            f"Directory does not exist: {out_dir}. Did you run persistence_plotter.py -pid first?"
        )
    if not os.path.exists(summary_path):
        _exit_with_warning(
            f"Missing {summary_path}. Did you run persistence_plotter.py -pid first?"
        )

    summary_df = pd.read_csv(summary_path, sep=";")

    # Apply config filtering if specified
    if config_indices is not None:
        summary_df = filter_summary_by_configs(summary_df, config_indices)

    # Ensure required columns exist
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")
    if "last_episode_cumulative_reward" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'last_episode_cumulative_reward'.")

    # Convert reward to numeric and sort by reward (descending)
    summary_df = summary_df.copy()
    summary_df["last_episode_cumulative_reward"] = pd.to_numeric(
        summary_df["last_episode_cumulative_reward"], errors="coerce"
    )
    if summary_df["last_episode_cumulative_reward"].isna().any():
        _exit_with_warning("summary.csv contains non-numeric last_episode_cumulative_reward values; aborting.")

    summary_df = summary_df.sort_values(
        by="last_episode_cumulative_reward",
        ascending=False,
        kind="mergesort"
    )

    log.info(LINE_LENGTH * "-")
    log.info(f"Compare-All mode: plotting {len(summary_df)} configurations")

    tmp: list[tuple[str, pd.DataFrame, str, str]] = []
    summary_entries: list[tuple[str, Optional[int], str, float]] = []
    for _, row in summary_df.iterrows():
        run_id = str(row["configuration_directory"])
        reward = row['last_episode_cumulative_reward']

        # Parse run_id to extract cfg index and all tokens for legend label
        cfg_idx = extract_cfg_index(run_id)
        cfg_str = f"cfg@{cfg_idx}" if cfg_idx is not None else run_id

        # Parse all tokens from run_id and build legend label
        overrides_str = ""
        color_key = ""
        try:
            pr = parse_run_id_strict(run_id)
            # Build legend label: cfg@N (abbr=value, abbr=value, ...)
            # Filter out ignored keys (cfg, cg, alg+runs)
            if pr.tokens:
                overrides = {k: v for k, v in pr.tokens.items() if k not in LIST_OF_IGNORED_OVERRIDES}
                overrides_str = build_overrides_str(overrides)
                color_key = build_color_key(overrides)
                legend_label = f'{cfg_str} ({overrides_str})' if overrides_str else cfg_str
            else:
                legend_label = cfg_str
        except SystemExit:
            # If parse_run_id_strict exits, use cfg_str as fallback
            legend_label = cfg_str

        log.info(f"  {cfg_str}: {run_id} | reward={reward:.2f}")
        summary_entries.append((legend_label, cfg_idx, run_id, reward))

        common_path = os.path.join(out_dir, run_id, "common_data.csv")
        if not os.path.exists(common_path):
            log.warning(f"Missing {common_path}. Skipping this run.")
            continue

        try:
            df = pd.read_csv(common_path, sep=";")
            tmp.append((legend_label, df, run_id, overrides_str))
        except Exception as e:
            log.warning(f"Error reading {common_path}: {e}. Skipping this run.")
            continue

    log.info(LINE_LENGTH * "-")

    if not tmp:
        _exit_with_warning("No valid runs found to plot.")

    series_by_label: list[tuple[str, pd.DataFrame, str, str]] = tmp

    comparisons = [
        ("currentEpisodeReward", "Current Episode Reward", "Episode", "Reward"),
        ("currentCumulativeReward", "Current Cumulative Reward", "Episode", "Reward"),
        ("currentTrueDetections", "Current True Detections", "Episode", "Detection"),
        ("currentUniqueDetections", "Current Unique True Detections", "Episode", "Detection"),
    ]

    for y_key, title, xlabel, ylabel in comparisons:
        out_file = os.path.join(out_dir, _sanitize_filename(f"Bulk Comparison of {title}.png"))
        plot_bestof_by_episode(
            series_by_label=series_by_label,
            y_key=y_key,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            out_file=out_file,
            suptitle=suptitle,
            legend_outside=legend_outside,
            legend_side=legend_side,
            annotate_diff=annotate_diff,
        )
        log.info(f"Saved: {out_file}")

    print_final_summary(
        summary_entries,
        heading=f"COMPARE-ALL SUMMARY (sorted by reward, highest first) {all_of}",
    )


def run_bestof(all_of: str, comparison_key: str, addparams: Union[dict[str, str], None] = None, suptitle: SuptitleFormat = None, config_indices: Union[list[int], None] = None, annotate_diff: bool = False, legend_outside: bool = False, legend_side: bool = False) -> None:
    out_dir = os.path.join(PLOT_RESULTS_DIR, all_of)
    summary_path = os.path.join(out_dir, "summary.csv")

    if not os.path.exists(out_dir):
        _exit_with_warning(
            f"Directory does not exist: {out_dir}. Did you run persistence_plotter.py -pid first?"
        )
    if not os.path.exists(summary_path):
        _exit_with_warning(
            f"Missing {summary_path}. Did you run persistence_plotter.py -pid first?"
        )

    summary_df = pd.read_csv(summary_path, sep=";")

    # Apply config filtering if specified
    if config_indices is not None:
        summary_df = filter_summary_by_configs(summary_df, config_indices)

    winners = best_of_by_group(summary_df, comparison_key, addparams)

    log.info(LINE_LENGTH * "-")
    log.info(f"Best-Of selection by group '{comparison_key}'")
    for _, row in winners.iterrows():
        gv = str(row["group_value"])
        formal = GROUP_VALUE_TERMS.get(gv, "")
        formal_part = f" ({formal})" if formal else ""
        last_reward = row['last_episode_cumulative_reward']
        log.info(
            f"{gv}{formal_part}: {row['configuration_directory']} | last_episode_cumulative_reward={last_reward:.2f}"
        )
    log.info(LINE_LENGTH * "-")

    tmp: list[tuple[str, str, pd.DataFrame, str, str]] = []
    for _, row in winners.iterrows():
        run_id = str(row["configuration_directory"])
        group_value = str(row["group_value"])
        label = str(row["legend_label"])
        color_key = str(row["overrides_key"])
        common_path = os.path.join(out_dir, run_id, "common_data.csv")
        if not os.path.exists(common_path):
            _exit_with_warning(
                f"Missing {common_path}. Generate it with persistence_plotter.py first."
            )
        df = pd.read_csv(common_path, sep=";")
        tmp.append((group_value, label, df, run_id, color_key))

    tmp.sort(key=lambda t: t[0])
    series_by_label: list[tuple[str, pd.DataFrame, str, str]] = [
        (label, df, run_id, color_key) for _, label, df, run_id, color_key in tmp
    ]

    comparisons = [
        ("currentEpisodeReward", "Current Episode Reward", "Episode", "Reward"),
        ("currentCumulativeReward", "Current Cumulative Reward", "Episode", "Reward"),
        ("currentTrueDetections", "Current True Detections", "Episode", "Detection"),
        ("currentUniqueDetections", "Current Unique True Detections", "Episode", "Detection"),
    ]

    for y_key, title, xlabel, ylabel in comparisons:
        out_file = os.path.join(out_dir, _sanitize_filename(f"Best-Of Comparison of {title}.png"))
        plot_bestof_by_episode(
            series_by_label=series_by_label,
            y_key=y_key,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            out_file=out_file,
            suptitle=suptitle,
            cmap=BESTOF_CMAP,
            legend_outside=legend_outside,
            legend_side=legend_side,
            annotate_diff=annotate_diff,
        )
        log.info(f"Saved: {out_file}")

    summary_entries: list[tuple[str, Optional[int], str, float]] = []
    for _, row in winners.iterrows():
        gv = str(row["group_value"])
        formal = GROUP_VALUE_TERMS.get(gv, "")
        name = f"{gv} ({formal})" if formal else gv
        run_id = str(row["configuration_directory"])
        summary_entries.append(
            (name, extract_cfg_index(run_id), run_id, row["last_episode_cumulative_reward"])
        )

    print_final_summary(
        summary_entries,
        heading=f"BEST-OF SUMMARY (grouped by '{comparison_key}') {all_of}",
    )


def run_configgroup(all_of: str, cg_key: str, suptitle: SuptitleFormat = None, config_indices: Union[list[int], None] = None, annotate_diff: bool = False, legend_outside: bool = False, legend_side: bool = False) -> None:
    """Compare all runs matching a config-group key.

    Filters runs by cg@KEY, plots all matching runs sorted by reward (descending).
    Legend labels show parameter overrides only (no cg@ or cfg@ prefixes).

    Args:
        all_of: Parent results directory under pyplotters/plots
        cg_key: The config-group value to filter by (e.g., 'ql_epsilon')
        suptitle: Optional custom title for plots
        config_indices: Optional list of config indices to additionally filter by
    """
    out_dir = os.path.join(PLOT_RESULTS_DIR, all_of)
    summary_path = os.path.join(out_dir, "summary.csv")

    if not os.path.exists(out_dir):
        _exit_with_warning(
            f"Directory does not exist: {out_dir}. Did you run persistence_plotter.py -pid first?"
        )
    if not os.path.exists(summary_path):
        _exit_with_warning(
            f"Missing {summary_path}. Did you run persistence_plotter.py -pid first?"
        )

    summary_df = pd.read_csv(summary_path, sep=";")

    # Filter by config-group key
    summary_df = filter_summary_by_configgroup(summary_df, cg_key)

    # Apply config filtering if specified (can combine with config-group filtering)
    if config_indices is not None:
        summary_df = filter_summary_by_configs(summary_df, config_indices)

    # Ensure required columns exist
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")
    if "last_episode_cumulative_reward" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'last_episode_cumulative_reward'.")

    # Convert reward to numeric and sort by reward (descending)
    summary_df = summary_df.copy()
    summary_df["last_episode_cumulative_reward"] = pd.to_numeric(
        summary_df["last_episode_cumulative_reward"], errors="coerce"
    )
    if summary_df["last_episode_cumulative_reward"].isna().any():
        _exit_with_warning("summary.csv contains non-numeric last_episode_cumulative_reward values; aborting.")

    summary_df = summary_df.sort_values(
        by="last_episode_cumulative_reward",
        ascending=False,
        kind="mergesort"
    )

    log.info(LINE_LENGTH * "-")
    log.info(f"Config-Group mode: cg@{cg_key}, plotting {len(summary_df)} runs")

    tmp: list[tuple[str, pd.DataFrame, str, str]] = []
    summary_entries: list[tuple[str, Optional[int], str, float]] = []
    for _, row in summary_df.iterrows():
        run_id = str(row["configuration_directory"])
        reward = row['last_episode_cumulative_reward']

        # Build legend label showing only parameter overrides (no cfg@, no cg@)
        overrides_str = ""
        color_key = ""
        try:
            pr = parse_run_id_strict(run_id)
            # Extract parameter overrides, excluding cfg, cg, and algorithm identifiers
            if pr.tokens:
                overrides = {k: v for k, v in pr.tokens.items() if k not in LIST_OF_IGNORED_OVERRIDES}
                overrides_str = build_overrides_str(overrides)
                color_key = build_color_key(overrides)
                legend_label = overrides_str if overrides_str else run_id
            else:
                legend_label = run_id
        except SystemExit:
            # If parse_run_id_strict exits, use run_id as fallback
            legend_label = run_id

        log.info(f"  {run_id} | reward={reward:.2f} | label={legend_label}")
        summary_entries.append((legend_label, extract_cfg_index(run_id), run_id, reward))

        common_path = os.path.join(out_dir, run_id, "common_data.csv")
        if not os.path.exists(common_path):
            log.warning(f"Missing {common_path}. Skipping this run.")
            continue

        try:
            df = pd.read_csv(common_path, sep=";")
            tmp.append((legend_label, df, run_id, color_key))
        except Exception as e:
            log.warning(f"Error reading {common_path}: {e}. Skipping this run.")
            continue

    log.info(LINE_LENGTH * "-")

    if not tmp:
        _exit_with_warning("No valid runs found to plot.")

    series_by_label: list[tuple[str, pd.DataFrame, str, str]] = tmp

    comparisons = [
        ("currentEpisodeReward", "Current Episode Reward", "Episode", "Reward"),
        ("currentCumulativeReward", "Current Cumulative Reward", "Episode", "Reward"),
        ("currentTrueDetections", "Current True Detections", "Episode", "Detection"),
        ("currentUniqueDetections", "Current Unique True Detections", "Episode", "Detection"),
    ]

    for y_key, title, xlabel, ylabel in comparisons:
        out_file = os.path.join(out_dir, _sanitize_filename(f"Bulk Comparison of {title} (of group {cg_key}).png"))
        plot_bestof_by_episode(
            series_by_label=series_by_label,
            y_key=y_key,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            out_file=out_file,
            suptitle=suptitle,
            legend_outside=legend_outside,
            legend_side=legend_side,
            annotate_diff=annotate_diff,
        )
        log.info(f"Saved: {out_file}")

    print_final_summary(
        summary_entries,
        heading=f"CONFIG-GROUP SUMMARY (cg@{cg_key}, sorted by reward, highest first) {all_of}",
    )


def main(argv: Union[list[str], None] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Best-of comparison plotter for ONE-Sim runs (uses pyplotters/plots outputs)."
    )
    parser.add_argument(
        "-pid",
        "--parent_id",
        type=str,
        required=True,
        help="Parent results directory under pyplotters/plots (same value used in persistence_plotter.py -pid).",
    )
    parser.add_argument(
        "--compareall",
        action="store_true",
        help="Compare all available configs instead of selecting best-of per group. --group becomes optional when this flag is set.",
    )
    parser.add_argument(
        "--comparekey",
        type=str,
        required=False,
        help="Grouping key to compare best-of runs (e.g. qlm_bp). Mutually exclusive with --compareall and --configgroup.",
    )
    parser.add_argument(
        "--configgroup",
        "-cg",
        type=str,
        required=False,
        help="Config-group key to filter runs by (e.g. ql_epsilon). Filters all runs matching cg@KEY. Mutually exclusive with --group and --compareall.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=str,
        required=False,
        help="Config indices to filter by (e.g. '1', '1-5', '1,3,5-7'). If not provided, all configs are processed.",
    )
    parser.add_argument(
        "--addparams",
        type=str,
        required=False,
        help="Comma-separated phantom parameters to inject into runs missing the group key (e.g. 'qlm_bp@lfe,other_key@value'). "
             "Only used in best-of mode (incompatible with --compareall and --configgroup).",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        required=False,
        help="Custom title for plots (appears as main suptitle, with subplot titles as subtitles).",
    )
    parser.add_argument(
        "-ad",
        "--annotatediff",
        action="store_true",
        help="Annotate episode-to-episode differences on the plot. Each line's annotations will use that line's color.",
    )
    parser.add_argument(
        "--legend-outside",
        action="store_true",
        default=False,
        help="Place the legend outside/below the plot as a single column (default: False = legend is placed inside the plot).",
    )
    parser.add_argument(
        "--legend-side",
        action="store_true",
        default=False,
        help="Place the legend on the right side of the plot as a single column.",
    )
    args = parser.parse_args(argv)

    # Count how many modes are specified (exactly one must be set)
    modes_specified = sum([bool(args.compareall), bool(args.comparekey), bool(args.configgroup)])

    if modes_specified != 1:
        _exit_with_warning(
            "Exactly one mode must be specified: --group, --compareall, or --configgroup"
        )

    if args.compareall and args.addparams:
        log.warning("--compareall flag is set; --addparams argument will be ignored.")

    # Parse and validate --config if provided
    config_indices: Union[list[int], None] = None
    if args.config:
        try:
            config_indices = parse_config_indices(args.config)
            log.info(f"Config filtering enabled: {args.config} → indices {config_indices}")
        except ValueError as e:
            _exit_with_warning(f"Invalid config format: {e}")

    if args.compareall and args.addparams:
        log.warning("--compareall flag is set; --addparams argument will be ignored.")

    # Parse and validate --addparams if provided (only used in best-of mode)
    addparams: Union[dict[str, str], None] = None
    if args.addparams and args.comparekey:
        addparams = {}
        params_list = args.addparams.split(",")
        for param in params_list:
            param = param.strip()
            if "@" not in param or param.count("@") != 1:
                _exit_with_warning(
                    f"Invalid addparam format '{param}'. Expected format: 'key@value' (comma-separated for multiple)."
                )
            key, value = param.split("@")
            if not key or not value:
                _exit_with_warning(
                    f"Invalid addparam '{param}': key or value is empty."
                )
            addparams[key] = value

        # Sort by key alphabetically for stable/deterministic injection order
        addparams = dict(sorted(addparams.items()))
        log.info(f"Phantom addparams provided: {addparams}")

    ftitle = SuptitleFormat("", 1)

    if args.title:
        # Replacing special newline escape character and \\t for latex equation
        args.title = (
            args.title
            .replace(r"\n", "\n")
            .replace(r"\\t", "\\t")
        )
        line_count = args.title.count("\n") + 1
        ftitle = SuptitleFormat(args.title, line_count)

    legend_outside: bool = args.legend_outside
    legend_side: bool = args.legend_side

    # Route to appropriate function
    if args.compareall:
        run_compareall(args.parent_id, ftitle, config_indices, args.annotatediff, legend_outside, legend_side)
    elif args.configgroup:
        run_configgroup(args.parent_id, args.configgroup, ftitle, config_indices, args.annotatediff, legend_outside, legend_side)
    else:
        run_bestof(args.parent_id, args.comparekey, addparams, ftitle, config_indices, args.annotatediff, legend_outside, legend_side)


class SuptitleFormat:
    def __init__(self, title: str, newline_gap: int = 1):
        self.title = title
        self.newline_gap = newline_gap

if __name__ == "__main__":
    main()