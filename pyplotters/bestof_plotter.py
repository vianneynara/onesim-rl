"""Best-of comparison plotter.

This script compares *already processed* runs under `pyplotters/plots/<aof>/...`.
It selects, for each value of a given group key (e.g. `qlm_bp`), the run with the
highest `max_cumulative_reward` (from `summary.csv`) and overlays their episode
series on a shared plot.

Assumptions / constraints (by design):
- Must be invoked with `-aof/--all_of`.
- Requires `pyplotters/plots/<aof>/summary.csv` to exist.
- Requires each referenced `common_data.csv` to exist.
- Run-directory names must be parseable as: <prefix>-<k>@<v>-<k>@<v>-...
  (prefix is ignored). If parsing fails, the script exits with a warning.

Example:
  python -m pyplotters.bestof_plotter -aof ql-c-ms@0-ls@0 --group qlm_bp
  python -m pyplotters.bestof_plotter -aof ql-c-ms@0-ls@0 --group qlm_bp -c 1-5
  python -m pyplotters.bestof_plotter -aof ql-c-ms@0-ls@0 --group qlm_bp -c 1,3,5-7

Outputs:
  Saves best-of comparison plots into `pyplotters/plots/<aof>/` adjacent to
  `summary.csv`.
"""

from __future__ import annotations

import argparse
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

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

PLOT_RESULTS_DIR = "pyplotters\\plots"
# PLOT_RESULTS_DIR = r"D:\Developments+\Java\onesim-rl-data\plots"


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


def key_to_abbr(key: str) -> str:
    """Convert an override key to its abbreviation.

    Example: "ucb_ec" -> "ec" (substring after last underscore)
             "ts_iv"  -> "iv"
             "foo"    -> "foo"
    """
    if "_" in key:
        return key.rsplit("_", 1)[-1]
    return key


def build_legend_label(group_value: str, overrides: dict[str, str]) -> str:
    """Build legend label in the form: '<group> (abbr=value, abbr=value)'.

    Overrides are sorted by abbreviation for stable legends.
    """
    # Expand group value with formal wording when available.
    group_display = GROUP_VALUE_TERMS.get(group_value, group_value)

    items: list[tuple[str, str]] = []
    for k, v in overrides.items():
        items.append((key_to_abbr(k), str(v)))
    items.sort(key=lambda t: t[0])

    overrides_str = ", ".join([f"{abbr}={val}" for abbr, val in items])
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
        
        overrides = {k: v for k, v in pr.tokens.items() if k != group_key}
        records.append(
            {
                "configuration_directory": run_id,
                "group_value": group_value,
                "legend_label": build_legend_label(group_value, overrides),
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


def plot_bestof_by_episode(
    series_by_label: list[tuple[str, pd.DataFrame]],
    y_key: str,
    title: str,
    xlabel: str,
    ylabel: str,
    out_file: str,
    suptitle: Union[str, None] = None,
):
    if not series_by_label:
        _exit_with_warning("No best-of series to plot.")

    plt.figure(figsize=(10, 6))

    max_ep = None
    min_ep = None
    for _, df in series_by_label:
        if "episodeNumber" not in df.columns:
            _exit_with_warning("common_data.csv missing required column 'episodeNumber'.")
        max_ep = int(df["episodeNumber"].max()) if max_ep is None else max(max_ep, int(df["episodeNumber"].max()))
        min_ep = int(df["episodeNumber"].min()) if min_ep is None else min(min_ep, int(df["episodeNumber"].min()))

    palette = sns.color_palette(n_colors=len(series_by_label))
    for (label, df), color in zip(series_by_label, palette):
        if y_key not in df.columns:
            _exit_with_warning(f"common_data.csv missing required column '{y_key}'.")
        sns.lineplot(data=df, x="episodeNumber", y=y_key, label=label, color=color)

    if max_ep is not None and min_ep is not None:
        if max_ep <= 20:
            ticks = np.arange(min_ep, max_ep + 1, 1)
        else:
            step = max(1, max_ep // 10)
            start = (min_ep // step) * step
            ticks = np.arange(start, max_ep + 1, step)
        plt.xticks(ticks)
        plt.xlim(left=min_ep)

    # Construct title with suptitle and subtitle
    if suptitle:
        # Multi-line title: suptitle on top, subtitle below
        fig = plt.gcf()
        fig.suptitle(suptitle, fontweight="bold", fontsize=12, y=0.99)
        plt.title(title, fontweight="bold", fontsize=10)
        fig.subplots_adjust(top=0.92)
    else:
        # Single title (backward compatible)
        plt.title(title, fontweight="bold")

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.margins(x=0)

    ax = plt.gca()
    handles, _labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles=handles, loc="best", prop={"family": "monospace"})

    out_dir = os.path.dirname(out_file)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    plt.savefig(out_file, bbox_inches="tight")
    plt.close()


def run_bestof(all_of: str, group_key: str, addparams: Union[dict[str, str], None] = None, suptitle: Union[str, None] = None, config_indices: Union[list[int], None] = None) -> None:
    out_dir = os.path.join(PLOT_RESULTS_DIR, all_of)
    summary_path = os.path.join(out_dir, "summary.csv")

    if not os.path.exists(out_dir):
        _exit_with_warning(
            f"Directory does not exist: {out_dir}. Did you run persistence_plotter.py -aof first?"
        )
    if not os.path.exists(summary_path):
        _exit_with_warning(
            f"Missing {summary_path}. Did you run persistence_plotter.py -aof first?"
        )

    summary_df = pd.read_csv(summary_path, sep=";")
    
    # Apply config filtering if specified
    if config_indices is not None:
        summary_df = filter_summary_by_configs(summary_df, config_indices)
    
    winners = best_of_by_group(summary_df, group_key, addparams)

    log.info(LINE_LENGTH * "-")
    log.info(f"Best-Of selection by group '{group_key}'")
    for _, row in winners.iterrows():
        gv = str(row["group_value"])
        formal = GROUP_VALUE_TERMS.get(gv, "")
        formal_part = f" ({formal})" if formal else ""
        last_reward = row['last_episode_cumulative_reward']
        log.info(
            f"{gv}{formal_part}: {row['configuration_directory']} | last_episode_cumulative_reward={last_reward:.2f}"
        )
    log.info(LINE_LENGTH * "-")

    tmp: list[tuple[str, str, pd.DataFrame]] = []
    for _, row in winners.iterrows():
        run_id = str(row["configuration_directory"])
        group_value = str(row["group_value"])
        label = str(row["legend_label"])
        common_path = os.path.join(out_dir, run_id, "common_data.csv")
        if not os.path.exists(common_path):
            _exit_with_warning(
                f"Missing {common_path}. Generate it with persistence_plotter.py first."
            )
        df = pd.read_csv(common_path, sep=";")
        tmp.append((group_value, label, df))

    tmp.sort(key=lambda t: t[0])
    series_by_label: list[tuple[str, pd.DataFrame]] = [(label, df) for _, label, df in tmp]

    comparisons = [
        ("currentEpisodeReward", "Current Episode Reward", "Episode", "Reward"),
        ("currentCumulativeReward", "Current Cumulative Reward", "Episode", "Reward"),
        ("currentTrueDetections", "Current True Detections", "Episode", "Detection"),
        ("currentUniqueDetections", "Current Unique Detections", "Episode", "Detection"),
    ]

    for y_key, title, xlabel, ylabel in comparisons:
        out_file = os.path.join(out_dir, _sanitize_filename(f"{title} (Best-Of Comparison).png"))
        plot_bestof_by_episode(
            series_by_label=series_by_label,
            y_key=y_key,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            out_file=out_file,
            suptitle=suptitle,
        )
        log.info(f"Saved: {out_file}")


def main(argv: Union[list[str], None] = None) -> None:
    parser = argparse.ArgumentParser(
        description="Best-of comparison plotter for ONE-Sim runs (uses pyplotters/plots outputs)."
    )
    parser.add_argument(
        "-aof",
        "--all_of",
        type=str,
        required=True,
        help="Parent results directory under pyplotters/plots (same value used in persistence_plotter.py -aof).",
    )
    parser.add_argument(
        "--group",
        type=str,
        required=True,
        help="Grouping key to compare best-of runs (e.g. qlm_bp).",
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
             "If a key already exists in a run-id, that injection is skipped with a warning.",
    )
    parser.add_argument(
        "-t",
        "--title",
        type=str,
        required=False,
        help="Custom title for plots (appears as main suptitle, with subplot titles as subtitles).",
    )

    args = parser.parse_args(argv)
    
    # Parse and validate --config if provided
    config_indices: Union[list[int], None] = None
    if args.config:
        try:
            config_indices = parse_config_indices(args.config)
            log.info(f"Config filtering enabled: {args.config} → indices {config_indices}")
        except ValueError as e:
            _exit_with_warning(f"Invalid config format: {e}")
    
    # Parse and validate --addparams if provided
    addparams: Union[dict[str, str], None] = None
    if args.addparams:
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
    
    run_bestof(args.all_of, args.group, addparams, args.title, config_indices)


if __name__ == "__main__":
    main()

