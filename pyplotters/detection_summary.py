"""
Detection Summary Extractor: Filters summary.csv by configuration number and exports detection metrics.
"""

import argparse
import logging
import os
import sys

import pandas as pd

# Import parse_parent_dir_ids from batch_shifter
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.batch_shifter import parse_parent_dir_ids

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_REPORTS_DIR = r"D:\Developments+\Java\onesim-rl-data\reports"
PLOT_RESULTS_DIR = r"D:\Developments+\Java\onesim-rl-data\plots"

OUTPUT_COLUMNS = [
    "configuration_directory",
    "group",
    "min_true_det",
    "avg_true_det",
    "max_true_det",
    "min_uniq_det",
    "avg_uniq_det",
    "max_uniq_det",
]


def parse_cfg_range(_cfg_string: str) -> set[int]:
    """
    Parse comma-separated config numbers with range support.
    
    Example: "1,3,5-7,10" -> {1, 3, 5, 6, 7, 10}
    Invalid entries are warned and skipped.
    
    Args:
        _cfg_string: Comma-separated config numbers, optionally with ranges
        
    Returns:
        Set of valid config numbers
    """
    if not _cfg_string:
        return set()
    
    cfg_set = set()
    entries = _cfg_string.split(",")
    
    for entry in entries:
        entry = entry.strip()
        
        if not entry:
            continue
        
        if "-" in entry:
            # Handle range
            try:
                parts = entry.split("-")
                if len(parts) == 2:
                    start = int(parts[0].strip())
                    end = int(parts[1].strip())
                    if start <= end:
                        cfg_set.update(range(start, end + 1))
                    else:
                        log.warning(f"Invalid range: {entry} (start > end), skipping")
                else:
                    log.warning(f"Invalid range format: {entry}, skipping")
            except ValueError:
                log.warning(f"Invalid range format: {entry}, skipping")
        else:
            # Single number
            try:
                cfg_num = int(entry)
                if cfg_num >= 0:
                    cfg_set.add(cfg_num)
                else:
                    log.warning(f"Invalid config number: {entry} (negative), skipping")
            except ValueError:
                log.warning(f"Invalid config number: {entry}, skipping")
    
    return cfg_set


def extract_cfg_number(_config_dir: str) -> int | None:
    """
    Extract cfg@N number from configuration_directory string.
    
    Example: "ql-movseed@0-cfg@02-cg@ql_epsilon" -> 2
    Returns None if cfg@ token not found or invalid.
    
    Args:
        _config_dir: Configuration directory name (run_id)
        
    Returns:
        Config number (int) or None if not found/invalid
    """
    tokens = _config_dir.split("-")
    
    for token in tokens:
        if "@" in token:
            key, value = token.split("@", 1)
            if key == "cfg":
                try:
                    return int(value)
                except ValueError:
                    log.warning(f"Invalid cfg number format: {value} in {_config_dir}")
                    return None
    
    return None


def check_exists_source_dir(dir_path):
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The base source directory {dir_path} does not exist.")


def process_detection_summary(_parent_id: str, _cfg_numbers: set[int]):
    """
    Read summary.csv, filter by cfg numbers, and save detection_summary.csv.
    
    Args:
        _parent_id: Parent directory ID
        _cfg_numbers: Set of config numbers to filter
    """
    log.info(LINE_LENGTH * "-")
    log.info(f"Processing parent_id: {_parent_id}")
    log.info(f"Filtering for cfg numbers: {sorted(_cfg_numbers)}")
    
    # Read summary.csv
    summary_csv_path = os.path.join(PLOT_RESULTS_DIR, _parent_id, "summary.csv")
    
    if not os.path.exists(summary_csv_path):
        log.error(f"summary.csv not found at: {summary_csv_path}")
        log.error("Please run persistence_plotter first to generate summary.csv")
        return False
    
    log.info(f"Reading summary.csv from: {summary_csv_path}")
    summary_df = pd.read_csv(summary_csv_path, sep=";")
    
    log.info(f"Total rows in summary.csv: {len(summary_df)}")
    
    # Extract cfg numbers and filter
    matched_rows = []
    unmatched_count = 0
    cfg_not_found_count = 0
    
    for idx, row in summary_df.iterrows():
        config_dir = row["configuration_directory"]
        cfg_num = extract_cfg_number(config_dir)
        
        if cfg_num is None:
            cfg_not_found_count += 1
            log.warning(f"No cfg number found in: {config_dir}, skipping")
            continue
        
        if cfg_num in _cfg_numbers:
            matched_rows.append(row)
        else:
            unmatched_count += 1
    
    log.info(f"Matched rows: {len(matched_rows)}")
    log.info(f"Unmatched rows: {unmatched_count}")
    log.info(f"Rows with missing cfg: {cfg_not_found_count}")
    
    if len(matched_rows) == 0:
        log.error("No rows matched the specified cfg numbers!")
        log.error(f"Specified: {sorted(_cfg_numbers)}")
        return False
    
    # Create filtered dataframe with selected columns
    filtered_df = pd.DataFrame(matched_rows)
    
    # Ensure all output columns exist
    for col in OUTPUT_COLUMNS:
        if col not in filtered_df.columns:
            log.warning(f"Column '{col}' not found in summary.csv, skipping")
    
    # Select only available columns from OUTPUT_COLUMNS
    available_cols = [col for col in OUTPUT_COLUMNS if col in filtered_df.columns]
    filtered_df = filtered_df[available_cols]
    
    # Save detection_summary.csv
    output_csv_path = os.path.join(PLOT_RESULTS_DIR, _parent_id, "detection_summary.csv")
    log.info(f"Saving detection_summary.csv to: {output_csv_path}")
    filtered_df.to_csv(output_csv_path, index=False, sep=";", header=True)
    
    log.info(f"Done processing parent_id: {_parent_id}")
    log.info(LINE_LENGTH * "=")
    
    return True


if __name__ == "__main__":
    check_exists_source_dir(PLOT_RESULTS_DIR)
    
    parser = argparse.ArgumentParser(
        description="Detection Summary Extractor: Filter summary.csv by configuration number and extract detection metrics."
    )
    
    parser.add_argument(
        "-pid", "--parent-id", type=str, required=True,
        help="Parent report directory/directories, comma-separated. (e.g. \"ql\" or \"ql-p-ms@0,ql-p-ms@1\")"
    )
    
    parser.add_argument(
        "-cfg", "--config", type=str, required=True,
        help="Config numbers to filter, comma-separated with range support. (e.g. \"1,3,5-7,10\")"
    )
    
    args = parser.parse_args()
    
    # Parse parent_dir_ids
    parent_dir_ids = parse_parent_dir_ids(args.parent_id)
    
    if not parent_dir_ids:
        log.error("No valid parent_dir_id(s) provided")
        parser.print_help()
        sys.exit(1)
    
    # Parse config numbers
    cfg_numbers = parse_cfg_range(args.config)
    
    if not cfg_numbers:
        log.error("No valid config numbers provided")
        parser.print_help()
        sys.exit(1)
    
    log.info(f"Processing {len(parent_dir_ids)} parent_dir_id(s): {parent_dir_ids}")
    
    # Process each parent_dir_id
    success_count = 0
    for parent_id in parent_dir_ids:
        try:
            if process_detection_summary(parent_id, cfg_numbers):
                success_count += 1
        except Exception as e:
            log.error(f"Error processing parent_id {parent_id}: {e}")
    
    log.info(f"Successfully processed {success_count}/{len(parent_dir_ids)} parent_dir_id(s)")
    
    if success_count == 0:
        sys.exit(1)

