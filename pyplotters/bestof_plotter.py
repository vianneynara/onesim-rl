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

Outputs:
  Saves best-of comparison plots into `pyplotters/plots/<aof>/` adjacent to
  `summary.csv`.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass

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
            _exit_with_warning(
                f"Run-id '{run_id}' contains invalid token '{raw}'. Expected exactly one '@'."
            )
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
    return f"{group_display} ({overrides_str})"


def best_of_by_group(summary_df: pd.DataFrame, group_key: str) -> pd.DataFrame:
    """Return DF with the single best run per group value."""
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")
    if "max_cumulative_reward" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'max_cumulative_reward'.")

    records: list[dict[str, str]] = []
    for run_id in summary_df["configuration_directory"].astype(str).tolist():
        pr = parse_run_id_strict(run_id)
        if group_key not in pr.tokens:
            _exit_with_warning(
                f"Run-id '{run_id}' does not contain required group key '{group_key}@...'."
            )
        group_value = pr.tokens[group_key]
        overrides = {k: v for k, v in pr.tokens.items() if k != group_key}
        records.append(
            {
                "configuration_directory": run_id,
                "group_value": group_value,
                "legend_label": build_legend_label(group_value, overrides),
            }
        )

    parsed_df = pd.DataFrame(records)
    merged = summary_df.merge(parsed_df, on="configuration_directory", how="left")

    merged = merged.copy()
    merged["max_cumulative_reward"] = pd.to_numeric(merged["max_cumulative_reward"], errors="coerce")
    if merged["max_cumulative_reward"].isna().any():
        _exit_with_warning("summary.csv contains non-numeric max_cumulative_reward values; aborting.")

    merged = merged.sort_values(
        by=["group_value", "max_cumulative_reward", "configuration_directory"],
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


def run_bestof(all_of: str, group_key: str) -> None:
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
    winners = best_of_by_group(summary_df, group_key)

    log.info(LINE_LENGTH * "-")
    log.info(f"Best-Of selection by group '{group_key}'")
    for _, row in winners.iterrows():
        gv = str(row["group_value"])
        formal = GROUP_VALUE_TERMS.get(gv, "")
        formal_part = f" ({formal})" if formal else ""
        log.info(
            f"{gv}{formal_part}: {row['configuration_directory']} | max_cumulative_reward={row['max_cumulative_reward']}"
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
        out_file = os.path.join(out_dir, _sanitize_filename(f"{title} (Best Of).png"))
        plot_bestof_by_episode(
            series_by_label=series_by_label,
            y_key=y_key,
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            out_file=out_file,
        )
        log.info(f"Saved: {out_file}")


def main(argv: list[str] | None = None) -> None:
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

    args = parser.parse_args(argv)
    run_bestof(args.all_of, args.group)


if __name__ == "__main__":
    main()

