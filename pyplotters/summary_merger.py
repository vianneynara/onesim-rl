"""Summary CSV merger utility.

This script merges summary.csv files from two runs (mergefrom → mergeto).
It concatenates rows from the source (mergefrom) into the destination (mergeto),
skipping duplicate entries based on the 'configuration_directory' column.

Optionally, with the --mvplots flag, it can also copy plot directories from mergefrom
to mergeto for each row being merged. The copied directories must contain common_data.csv
or the operation will fail with an error. Existing directories in mergeto are replaced
with a visible warning.

Assumptions / constraints (by design):
- Both --mergefrom and --mergeto must be provided together.
- Both run directories must exist under pyplotters/plots/<run_id>/.
- Both summary.csv files must exist and be non-empty.
- Duplicate rows are identified by 'configuration_directory' column;
  rows from mergefrom that duplicate mergeto rows are skipped.
- The mergeto summary.csv is overwritten in-place with the merged result.
- (With --mvplots) All directories being merged must contain common_data.csv.
- (With --mvplots) Existing directories in mergeto are replaced after warning.

Example:
  python -m pyplotters.summary_merger -mf ql-c-ms@0 -mt ql-c-ms@1
  python -m pyplotters.summary_merger -mf ql-c-ms@0 -mt ql-c-ms@1 --mvplots

Outputs:
  Overwrites pyplotters/plots/<mergeto>/summary.csv with merged data.
  (With --mvplots) Copies plot directories from mergefrom to mergeto.
"""

from __future__ import annotations

import argparse
import logging
import os
import shutil
import sys

import pandas as pd

# Allow running this file as a script (python pyplotters/summary_merger.py) while still
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

PLOT_RESULTS_DIR = "pyplotters\\plots"


def _exit_with_warning(msg: str, code: int = 2) -> None:
    log.warning(msg)
    raise SystemExit(code)


def _resolve_run_id_path(run_id: str) -> str:
    """Resolve a run-id to its full path under PLOT_RESULTS_DIR."""
    return os.path.join(PLOT_RESULTS_DIR, run_id)


def _get_summary_csv_path(run_id: str) -> str:
    """Get the full path to a run's summary.csv file."""
    return os.path.join(_resolve_run_id_path(run_id), "summary.csv")


def _copy_plot_directories(
    mergefrom_id: str,
    mergeto_id: str,
    config_dirs: list[str],
) -> None:
    """Copy plot directories from mergefrom to mergeto for each configuration.
    
    Args:
        mergefrom_id: Source run ID
        mergeto_id: Destination run ID
        config_dirs: List of configuration directory names to copy
    
    Raises:
        SystemExit: If a source directory lacks common_data.csv or if copy fails
    """
    mergefrom_base = _resolve_run_id_path(mergefrom_id)
    mergeto_base = _resolve_run_id_path(mergeto_id)
    
    log.info(f"Copying {len(config_dirs)} plot directories from '{mergefrom_id}' to '{mergeto_id}'")
    log.info(LINE_LENGTH * "-")
    
    for config_dir in config_dirs:
        src_dir = os.path.join(mergefrom_base, config_dir)
        dst_dir = os.path.join(mergeto_base, config_dir)
        
        # Verify that common_data.csv exists in source directory
        common_data_src = os.path.join(src_dir, "common_data.csv")
        if not os.path.exists(common_data_src):
            _exit_with_warning(
                f"ERROR: common_data.csv not found in source directory: {src_dir}"
            )
        
        # If destination directory exists, warn and delete it
        if os.path.exists(dst_dir):
            log.warning(
                f"[WARNING] Replacing existing directory: {dst_dir}"
            )
            shutil.rmtree(dst_dir)
        
        # Copy the directory
        try:
            shutil.copytree(src_dir, dst_dir)
            log.info(f"Copied: {config_dir}")
        except Exception as e:
            _exit_with_warning(
                f"ERROR: Failed to copy directory {src_dir} to {dst_dir}: {e}"
            )
    
    log.info(LINE_LENGTH * "-")
    log.info(f"Successfully copied {len(config_dirs)} plot directories.")


def run_merge(
    mergefrom_id: str,
    mergeto_id: str,
    mvplots: bool = False,
) -> None:
    """Merge summary.csv from mergefrom run into mergeto run.
    
    Args:
        mergefrom_id: Source run ID (data will be read from here)
        mergeto_id: Destination run ID (data will be merged into here)
        mvplots: If True, also copy plot directories containing common_data.csv
    
    Raises:
        SystemExit: If validation or file I/O fails
    """
    
    # Resolve paths
    mergefrom_path = _get_summary_csv_path(mergefrom_id)
    mergeto_path = _get_summary_csv_path(mergeto_id)
    
    # Validate that both paths exist
    if not os.path.exists(mergefrom_path):
        _exit_with_warning(
            f"Merge source summary.csv does not exist: {mergefrom_path}"
        )
    
    if not os.path.exists(mergeto_path):
        _exit_with_warning(
            f"Merge destination summary.csv does not exist: {mergeto_path}"
        )
    
    # Read both CSV files
    log.info(f"Reading source summary.csv: {mergefrom_path}")
    mergefrom_df = pd.read_csv(mergefrom_path, sep=";")
    
    if mergefrom_df.empty:
        _exit_with_warning(
            f"Source summary.csv is empty: {mergefrom_path}"
        )
    
    log.info(f"Reading destination summary.csv: {mergeto_path}")
    mergeto_df = pd.read_csv(mergeto_path, sep=";")
    
    if mergeto_df.empty:
        _exit_with_warning(
            f"Destination summary.csv is empty: {mergeto_path}"
        )
    
    # Validate that 'configuration_directory' column exists in both
    if "configuration_directory" not in mergefrom_df.columns:
        _exit_with_warning(
            f"Source summary.csv missing 'configuration_directory' column: {mergefrom_path}"
        )
    
    if "configuration_directory" not in mergeto_df.columns:
        _exit_with_warning(
            f"Destination summary.csv missing 'configuration_directory' column: {mergeto_path}"
        )
    
    # Log initial state
    log.info(LINE_LENGTH * "-")
    log.info(f"Merging '{mergefrom_id}' into '{mergeto_id}'")
    log.info(f"Source rows: {len(mergefrom_df)}")
    log.info(f"Destination rows (before merge): {len(mergeto_df)}")
    
    # Get set of existing configuration_directory values in mergeto
    existing_configs = set(mergeto_df["configuration_directory"].astype(str))
    
    # Filter mergefrom to only include rows that don't exist in mergeto
    mergefrom_configs = mergefrom_df["configuration_directory"].astype(str)
    rows_to_merge = mergefrom_df[~mergefrom_configs.isin(existing_configs)]
    
    duplicates_skipped = len(mergefrom_df) - len(rows_to_merge)
    
    log.info(f"Duplicates skipped: {duplicates_skipped}")
    log.info(f"New rows to merge: {len(rows_to_merge)}")
    
    # Concatenate dataframes
    merged_df = pd.concat([mergeto_df, rows_to_merge], ignore_index=True)
    
    log.info(f"Destination rows (after merge): {len(merged_df)}")
    
    # Write back to mergeto's summary.csv, overwriting in-place
    log.info(f"Writing merged summary to: {mergeto_path}")
    merged_df.to_csv(mergeto_path, index=False, sep=";", header=True)
    
    # If --mvplots is enabled, copy plot directories for merged rows
    if mvplots:
        # Extract list of configuration_directory names from rows_to_merge
        config_dirs_to_copy = rows_to_merge["configuration_directory"].astype(str).tolist()
        if config_dirs_to_copy:
            _copy_plot_directories(mergefrom_id, mergeto_id, config_dirs_to_copy)
        else:
            log.info("No new rows to merge; skipping plot directory copy.")
    
    log.info(LINE_LENGTH * "-")
    log.info("Merge complete.")
    log.info(LINE_LENGTH * "-")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Merge summary.csv files from two runs (source → destination)."
    )
    parser.add_argument(
        "-mf",
        "--mergefrom",
        type=str,
        required=False,
        help="Source run ID under pyplotters/plots/ (e.g. ql-c-ms@0).",
    )
    parser.add_argument(
        "-mt",
        "--mergeto",
        type=str,
        required=False,
        help="Destination run ID under pyplotters/plots/ (e.g. ql-c-ms@1).",
    )
    parser.add_argument(
        "--mvplots",
        action="store_true",
        help="Also copy plot directories containing common_data.csv from mergefrom to mergeto.",
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
    
    run_merge(args.mergefrom, args.mergeto, mvplots=args.mvplots)


if __name__ == "__main__":
    main()

