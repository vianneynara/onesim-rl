"""Evaluation CSV merger utility.

This script merges reward-evaluation.csv files from two runs (mergefrom → mergeto).
It appends rows from the source (mergefrom) into the destination (mergeto),
skipping duplicate entries based on the composite key of 'configuration' and 'group'.

Assumptions / constraints (by design):
- Both --mergefrom and --mergeto must be provided together.
- Both run directories must exist under PLOT_RESULTS_DIR/<run_id>/.
- Both reward-evaluation.csv files must exist and be non-empty.
- Duplicate rows are identified by the ('configuration', 'group') composite key;
  rows from mergefrom that duplicate mergeto entries are skipped.
- The mergeto reward-evaluation.csv is overwritten in-place with the merged result.
- Expected columns (EVAL_KEYS):
    configuration, group,
    min_episodic_reward, max_episodic_reward,
    avg_episodic_reward, std_episodic_reward

Example:
  python pyplotters/eval_merger.py -mf lfe-c-ms@0 -mt ql-c-ms@0

Outputs:
  Overwrites PLOT_RESULTS_DIR/<mergeto>/reward-evaluation.csv with merged data.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

import pandas as pd

# Allow running this file as a script (python pyplotters/eval_merger.py) while still
# using absolute package imports (pyplotters.*).
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

PLOT_RESULTS_DIR = r"D:\Developments+\Java\onesim-rl-data\plots"

EVAL_KEYS = [
    "configuration",
    "group",
    "min_episodic_reward",
    "max_episodic_reward",
    "avg_episodic_reward",
    "std_episodic_reward",
    "ci95_episodic_reward",
]

# Composite key used to detect duplicates
DEDUP_KEY = ["configuration", "group"]

EVAL_FILENAME = "reward-evaluation.csv"


def _exit_with_warning(msg: str, code: int = 2) -> None:
    log.warning(msg)
    raise SystemExit(code)


def _resolve_run_id_path(run_id: str) -> str:
    """Resolve a run-id to its full path under PLOT_RESULTS_DIR."""
    return os.path.join(PLOT_RESULTS_DIR, run_id)


def _get_eval_csv_path(run_id: str) -> str:
    """Get the full path to a run's reward-evaluation.csv file."""
    return os.path.join(_resolve_run_id_path(run_id), EVAL_FILENAME)


def _validate_eval_columns(df: pd.DataFrame, path: str) -> None:
    """Ensure all expected EVAL_KEYS columns are present in the dataframe."""
    missing = [col for col in EVAL_KEYS if col not in df.columns]
    if missing:
        _exit_with_warning(
            f"reward-evaluation.csv at '{path}' is missing expected columns: {missing}"
        )


def run_merge(
    mergefrom_id: str,
    mergeto_id: str,
) -> None:
    """Merge reward-evaluation.csv from mergefrom run into mergeto run.

    Args:
        mergefrom_id: Source run ID (data will be read from here)
        mergeto_id: Destination run ID (data will be merged into here)

    Raises:
        SystemExit: If validation or file I/O fails
    """

    # Resolve paths
    mergefrom_path = _get_eval_csv_path(mergefrom_id)
    mergeto_path = _get_eval_csv_path(mergeto_id)

    # Validate that both paths exist
    if not os.path.exists(mergefrom_path):
        _exit_with_warning(
            f"Merge source {EVAL_FILENAME} does not exist: {mergefrom_path}"
        )

    if not os.path.exists(mergeto_path):
        _exit_with_warning(
            f"Merge destination {EVAL_FILENAME} does not exist: {mergeto_path}"
        )

    # Read both CSV files
    log.info(f"Reading source {EVAL_FILENAME}: {mergefrom_path}")
    mergefrom_df = pd.read_csv(mergefrom_path, sep=";")

    if mergefrom_df.empty:
        _exit_with_warning(
            f"Source {EVAL_FILENAME} is empty: {mergefrom_path}"
        )

    log.info(f"Reading destination {EVAL_FILENAME}: {mergeto_path}")
    mergeto_df = pd.read_csv(mergeto_path, sep=";")

    if mergeto_df.empty:
        _exit_with_warning(
            f"Destination {EVAL_FILENAME} is empty: {mergeto_path}"
        )

    # Validate expected columns in both dataframes
    _validate_eval_columns(mergefrom_df, mergefrom_path)
    _validate_eval_columns(mergeto_df, mergeto_path)

    # Log initial state
    log.info(LINE_LENGTH * "-")
    log.info(f"Merging '{mergefrom_id}' into '{mergeto_id}'")
    log.info(f"Source rows: {len(mergefrom_df)}")
    log.info(f"Destination rows (before merge): {len(mergeto_df)}")

    # Build a set of existing composite keys in mergeto
    existing_keys = set(
        zip(
            mergeto_df["configuration"].astype(str),
            mergeto_df["group"].astype(str),
        )
    )

    # Filter mergefrom to only include rows whose composite key doesn't exist in mergeto
    mergefrom_keys = list(
        zip(
            mergefrom_df["configuration"].astype(str),
            mergefrom_df["group"].astype(str),
        )
    )
    new_rows_mask = [key not in existing_keys for key in mergefrom_keys]
    rows_to_merge = mergefrom_df[new_rows_mask]

    duplicates_skipped = len(mergefrom_df) - len(rows_to_merge)

    log.info(f"Duplicates skipped: {duplicates_skipped}")
    log.info(f"New rows to merge: {len(rows_to_merge)}")

    if rows_to_merge.empty:
        log.info("Nothing new to merge. Destination file left unchanged.")
        log.info(LINE_LENGTH * "-")
        log.info("Merge complete (no-op).")
        log.info(LINE_LENGTH * "-")
        return

    # Log which (configuration, group) pairs will be appended
    for _, row in rows_to_merge.iterrows():
        log.info(f"  + ({row['configuration']}, {row['group']})")

    # Concatenate dataframes
    merged_df = pd.concat([mergeto_df, rows_to_merge], ignore_index=True)

    log.info(f"Destination rows (after merge): {len(merged_df)}")

    # Write back to mergeto's reward-evaluation.csv, overwriting in-place
    log.info(f"Writing merged evaluation to: {mergeto_path}")
    merged_df.to_csv(mergeto_path, index=False, sep=";", header=True)

    log.info(LINE_LENGTH * "-")
    log.info("Merge complete.")
    log.info(LINE_LENGTH * "-")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description=(
            f"Merge {EVAL_FILENAME} files from two runs (source → destination)."
        )
    )
    parser.add_argument(
        "-mf",
        "--mergefrom",
        type=str,
        required=False,
        help="Source run ID under PLOT_RESULTS_DIR/ (e.g. lfe-c-ms@0).",
    )
    parser.add_argument(
        "-mt",
        "--mergeto",
        type=str,
        required=False,
        help="Destination run ID under PLOT_RESULTS_DIR/ (e.g. ql-c-ms@0).",
    )

    args = parser.parse_args(argv)

    # Validate that both arguments are provided together
    if args.mergefrom is None and args.mergeto is None:
        parser.print_help()
        sys.exit(0)

    if args.mergefrom is None:
        _exit_with_warning(
            "Argument --mergefrom (-mf) is required when --mergeto (-mt) is provided."
        )

    if args.mergeto is None:
        _exit_with_warning(
            "Argument --mergeto (-mt) is required when --mergefrom (-mf) is provided."
        )

    run_merge(args.mergefrom, args.mergeto)


if __name__ == "__main__":
    main()