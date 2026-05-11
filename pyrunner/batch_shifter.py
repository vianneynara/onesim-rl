"""
Batch Shifter: Automatically rename cfg@N prefixed run-id folders when batch configs are reordered/commented.

This module renames existing run-id folders to match the current active configs in LIST_OF_CONFIGS,
accounting for gaps created by commented-out or deleted configs.

Example:
  If configs 3-4 are commented out, cfg@5 becomes cfg@3, cfg@6 becomes cfg@4, etc.

Usage:
  python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0 --dry-run
  python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0
  python pyrunner/batch_shifter.py --all --dry-run
  python pyrunner/batch_shifter.py --all --indexonly --dry-run
"""

# ------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------------------------------------------- #

import argparse
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from typing import Optional, Tuple, List, Dict

# Allow running this file as a script
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.batch_configs import LIST_OF_CONFIGS

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------------------------------------------- #
# CONSTANTS
# ------------------------------------------------------------------------------------------------------------------- #

REPORTS_BASE = "reports/skripsi"
REPORTS_SHIFTED = "reports/_shifted"


# ------------------------------------------------------------------------------------------------------------------- #
# FUNCTIONS
# ------------------------------------------------------------------------------------------------------------------- #

def extract_cfg_index(folder_name: str) -> Optional[int]:
    """Extract cfg index from folder name like 'cfg@05-ql500-...'."""
    match = re.match(r"cfg@(\d+)", folder_name)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None


def extract_alg_and_runs(folder_name: str) -> Optional[Tuple[str, int]]:
    """
    Extract algorithm and runs from folder name like 'cfg@05-ql500-...' or 'cfg@05-lfe500-...'.
    Returns: (alg, runs) tuple or None if not found.
    """
    # Pattern: cfg@NN-ALG[digits]-...
    match = re.match(r"cfg@\d+-(\w+?)(\d+)", folder_name)
    if match:
        alg = match.group(1)
        try:
            runs = int(match.group(2))
            return alg, runs
        except ValueError:
            pass
    return None


def build_config_signature(alg: str, runs: int) -> str:
    """Build a signature from algorithm and runs (e.g., 'ql500')."""
    return f"{alg}{runs}"


def get_active_configs_mapping() -> Dict[int, dict]:
    """
    Build a mapping of config index to config dict for all active (uncommented) configs.
    Index is 1-based (matches cfg@N numbering).
    
    Returns: {config_index: config_dict, ...}
    """
    mapping = {}
    for idx, config in enumerate(LIST_OF_CONFIGS, start=1):
        mapping[idx] = config
    return mapping


def validate_config_match(
        folder_sig: Tuple[str, int],
        config_sig: str,
        index_only: bool = False
) -> bool:
    """
    Check if a folder signature matches a config signature.
    
    If index_only=False (default): validate alg + runs match the config signature.
    If index_only=True: no validation, assume index-based matching.
    """
    if index_only:
        return True
    
    # Extract from config signature (e.g., 'ql500')
    config_alg_runs = config_sig
    
    # Build folder signature (e.g., 'ql500')
    folder_alg, folder_runs = folder_sig
    folder_sig_str = build_config_signature(folder_alg, folder_runs)
    
    return folder_sig_str == config_alg_runs


def scan_run_id_folders(parent_dir_id: str) -> Dict[int, str]:
    """
    Scan run-id directory and extract all cfg@N folders.
    
    Returns: {cfg_index: folder_name, ...}
    Example: {31: 'cfg@31-ql500-qlm_bp@ts-ts_iv@5.0', 32: 'cfg@32-ql500-...'}
    """
    run_id_path = os.path.join(REPORTS_BASE, parent_dir_id, "run-id")
    
    if not os.path.isdir(run_id_path):
        log.warning("Run-id directory not found: %s", run_id_path)
        return {}
    
    cfg_folders = {}
    for folder_name in os.listdir(run_id_path):
        folder_path = os.path.join(run_id_path, folder_name)
        if not os.path.isdir(folder_path):
            continue
        
        cfg_idx = extract_cfg_index(folder_name)
        if cfg_idx is not None:
            cfg_folders[cfg_idx] = folder_name
    
    return cfg_folders


def build_rename_mapping(
        existing_folders: Dict[int, str],
        active_configs: Dict[int, dict],
        index_only: bool = False
) -> Tuple[Dict[int, int], List[str]]:
    """
    Build a mapping from old cfg index to new cfg index, validating matches.
    
    Returns: (rename_mapping, problems)
    - rename_mapping: {old_index: new_index, ...}
    - problems: list of warning/info messages
    """
    rename_mapping = {}
    problems = []
    
    # List of existing cfg indices, sorted
    existing_indices = sorted(existing_folders.keys())
    
    # List of active cfg indices (1, 2, 3, ..., len(active_configs))
    active_indices = sorted(active_configs.keys())
    
    log.info("Active config indices: %s", active_indices)
    log.info("Existing folder indices: %s", existing_indices)
    
    # Try to match existing folders to active configs
    # Strategy: iterate through existing folders and match them to active configs
    # based on alg+runs signature (unless index_only is True)
    
    matched = set()
    
    for old_idx in existing_indices:
        folder_name = existing_folders[old_idx]
        alg_runs_sig = extract_alg_and_runs(folder_name)
        
        if alg_runs_sig is None:
            problems.append(f"Could not extract alg+runs from folder: {folder_name}")
            continue
        
        # Find a matching active config
        found = False
        for new_idx in active_indices:
            if new_idx in matched:
                # Already assigned to another folder
                continue
            
            active_config = active_configs[new_idx]
            active_alg = active_config["alg"]
            active_runs = active_config["runs"]
            active_sig = build_config_signature(active_alg, active_runs)
            
            # Validate match
            if validate_config_match(alg_runs_sig, active_sig, index_only):
                # Check if this is the same config (same alg+runs)
                if index_only or extract_cfg_index(folder_name) == old_idx:
                    # For now, match if signatures match or index_only
                    # But we need to be smarter: match based on actual config content
                    # For simplicity without full validation, use the order
                    pass
        
        # If index_only, use sequential matching
        if index_only and old_idx <= len(active_indices):
            rename_mapping[old_idx] = old_idx
            matched.add(old_idx)
        else:
            # Match by finding the next unmatched active config with same alg+runs
            for new_idx in active_indices:
                if new_idx in matched:
                    continue
                
                active_config = active_configs[new_idx]
                active_alg = active_config["alg"]
                active_runs = active_config["runs"]
                active_sig = build_config_signature(active_alg, active_runs)
                
                folder_alg, folder_runs = alg_runs_sig
                if folder_alg == active_alg and folder_runs == active_runs:
                    rename_mapping[old_idx] = new_idx
                    matched.add(new_idx)
                    found = True
                    break
            
            if not found:
                problems.append(
                    f"No matching active config for folder index {old_idx} "
                    f"(alg={alg_runs_sig[0]}, runs={alg_runs_sig[1]})"
                )
    
    return rename_mapping, problems


def move_to_archive(src_path: str, archive_base: str) -> Tuple[bool, str]:
    """
    Move a folder to the _shifted archive directory.
    
    Returns: (success, message)
    """
    if not os.path.isdir(src_path):
        return False, f"Source path not found: {src_path}"
    
    # Extract components from src_path
    # Example: reports/skripsi/ql-p-ms@0/run-id/cfg@05-ql500-...
    parts = src_path.replace("\\", "/").split("/")
    
    if len(parts) < 5:
        return False, f"Invalid path structure: {src_path}"
    
    parent_dir_id = parts[2]  # ql-p-ms@0
    folder_name = parts[4]    # cfg@05-ql500-...
    
    archive_path = os.path.join(
        archive_base,
        parent_dir_id,
        "run-id"
    )
    
    os.makedirs(archive_path, exist_ok=True)
    
    dst_path = os.path.join(archive_path, folder_name)
    
    # Check if destination exists
    if os.path.exists(dst_path):
        return False, f"Archive destination already exists: {dst_path}"
    
    try:
        shutil.move(src_path, dst_path)
        return True, f"Moved {src_path} → {dst_path}"
    except Exception as e:
        return False, f"Failed to move {src_path}: {e}"


def rename_folder(old_path: str, old_name: str, new_name: str) -> Tuple[bool, str]:
    """Rename a folder from old_name to new_name."""
    new_path = os.path.join(os.path.dirname(old_path), new_name)
    
    if os.path.exists(new_path):
        return False, f"Destination already exists: {new_path}"
    
    try:
        os.rename(old_path, new_path)
        return True, f"Renamed {old_name} → {new_name}"
    except Exception as e:
        return False, f"Failed to rename: {e}"


def execute_shift(
        parent_dir_id: str,
        index_only: bool = False,
        dry_run: bool = False,
        no_archive: bool = False
) -> Tuple[int, int]:
    """
    Execute the shift operation for a specific parent_dir_id.
    
    Returns: (renamed_count, skipped_count)
    """
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Processing parent_dir_id: %s", parent_dir_id)
    log.info("=" * LINE_LENGTH)
    
    # Verify parent_dir_id exists
    pid_path = os.path.join(REPORTS_BASE, parent_dir_id)
    if not os.path.isdir(pid_path):
        log.warning("Parent dir not found: %s", pid_path)
        return 0, 0
    
    # Get active configs
    active_configs = get_active_configs_mapping()
    
    # Scan existing folders
    existing_folders = scan_run_id_folders(parent_dir_id)
    
    if not existing_folders:
        log.warning("No cfg@N folders found in %s", parent_dir_id)
        return 0, 0
    
    # Build rename mapping
    rename_mapping, problems = build_rename_mapping(
        existing_folders,
        active_configs,
        index_only
    )
    
    if problems:
        log.warning("Mapping issues:")
        for p in problems:
            log.warning("  - %s", p)
    
    renamed_count = 0
    skipped_count = 0
    
    if not rename_mapping:
        log.warning("No renames needed (or no valid mappings found)")
        return 0, len(existing_folders)
    
    # Sort by old index for processing
    for old_idx in sorted(rename_mapping.keys()):
        new_idx = rename_mapping[old_idx]
        old_folder_name = existing_folders[old_idx]
        
        if old_idx == new_idx:
            log.info("✓ Index %02d: No change needed (%s)", old_idx, old_folder_name)
            skipped_count += 1
            continue
        
        # Build new folder name by replacing cfg@XX
        new_folder_name = re.sub(r"cfg@\d+", f"cfg@{new_idx:02d}", old_folder_name)
        
        old_path = os.path.join(REPORTS_BASE, parent_dir_id, "run-id", old_folder_name)
        new_path = os.path.join(REPORTS_BASE, parent_dir_id, "run-id", new_folder_name)
        
        if dry_run:
            log.info(
                "DRY RUN: Index %02d → %02d: %s → %s",
                old_idx, new_idx, old_folder_name, new_folder_name
            )
            if not no_archive:
                log.info("  (would archive to: %s)", os.path.join(REPORTS_SHIFTED, parent_dir_id, "run-id", old_folder_name))
            renamed_count += 1
        else:
            # Archive old folder if not no_archive
            if not no_archive:
                ok, msg = move_to_archive(old_path, REPORTS_SHIFTED)
                if ok:
                    log.info("ARCHIVE: %s", msg)
                else:
                    log.error("ARCHIVE FAILED: %s", msg)
                    skipped_count += 1
                    continue
            else:
                # In-place rename: just rename the old folder directly
                ok, msg = rename_folder(old_path, old_folder_name, new_folder_name)
                if ok:
                    log.info("RENAMED: %s", msg)
                    renamed_count += 1
                else:
                    log.error("RENAME FAILED: %s", msg)
                    skipped_count += 1
    
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Summary for %s: %d renamed, %d skipped", parent_dir_id, renamed_count, skipped_count)
    log.info("%s", "=" * LINE_LENGTH)
    
    return renamed_count, skipped_count


def parse_parent_dir_ids(pid_string: str) -> List[str]:
    """
    Parse comma-separated parent_dir_ids from input string.
    
    Returns: List of parent_dir_ids (stripped of whitespace)
    Example: "ql-p-ms@0,ql-p-ms@1" → ["ql-p-ms@0", "ql-p-ms@1"]
    """
    if not pid_string:
        return []
    
    pids = [pid.strip() for pid in pid_string.split(",")]
    return [pid for pid in pids if pid]  # Filter out empty strings


# ------------------------------------------------------------------------------------------------------------------- #
# MAIN
# ------------------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch Shifter: Rename cfg@N folders when batch configs are reordered/commented"
    )
    
    parser.add_argument(
        "-pid", "--parent-dir-id", type=str, required=False,
        help="Process specific parent_dir_id(s) separated by comma (e.g., 'ql-p-ms@0' or 'ql-p-ms@0,ql-p-ms@1')"
    )
    
    parser.add_argument(
        "-a", "--all", action="store_true",
        help="Process all parent_dir_ids in reports/skripsi/"
    )
    
    parser.add_argument(
        "--indexonly", action="store_true",
        help="Match configs by index only (less strict validation)"
    )
    
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview changes without actually moving/renaming"
    )
    
    parser.add_argument(
        "--no-archive", action="store_true",
        help="Rename in-place without archiving old folders to _shifted"
    )
    
    args = parser.parse_args()
    
    # Validation
    if not args.all and not args.parent_dir_id:
        log.error("Specify either --parent-dir-id or --all")
        sys.exit(1)
    
    if args.all and args.parent_dir_id:
        log.error("Cannot specify both --all and --parent-dir-id")
        sys.exit(1)
    
    # Check if reports directory exists
    if not os.path.isdir(REPORTS_BASE):
        log.error("Reports directory not found: %s", REPORTS_BASE)
        sys.exit(1)
    
    total_renamed = 0
    total_skipped = 0
    
    if args.all:
        # Find all parent_dir_ids
        parent_dir_ids = []
        for item in os.listdir(REPORTS_BASE):
            item_path = os.path.join(REPORTS_BASE, item)
            if os.path.isdir(item_path):
                parent_dir_ids.append(item)
        
        if not parent_dir_ids:
            log.warning("No parent_dir_ids found in %s", REPORTS_BASE)
            sys.exit(0)
        
        log.info("Found %d parent_dir_ids: %s", len(parent_dir_ids), parent_dir_ids)
        
        for pid in sorted(parent_dir_ids):
            renamed, skipped = execute_shift(
                pid,
                index_only=args.indexonly,
                dry_run=args.dry_run,
                no_archive=args.no_archive
            )
            total_renamed += renamed
            total_skipped += skipped
    else:
        # Parse comma-separated parent_dir_ids
        parent_dir_ids = parse_parent_dir_ids(args.parent_dir_id)
        
        if not parent_dir_ids:
            log.error("No valid parent_dir_ids provided")
            sys.exit(1)
        
        log.info("Processing %d parent_dir_id(s): %s", len(parent_dir_ids), parent_dir_ids)
        
        for pid in parent_dir_ids:
            renamed, skipped = execute_shift(
                pid,
                index_only=args.indexonly,
                dry_run=args.dry_run,
                no_archive=args.no_archive
            )
            total_renamed += renamed
            total_skipped += skipped
    
    # Final summary
    log.info("%s", "=" * LINE_LENGTH)
    if args.dry_run:
        log.info("[DRY RUN] Total: %d would be renamed, %d skipped", total_renamed, total_skipped)
    else:
        log.info("[EXECUTION] Total: %d renamed, %d skipped", total_renamed, total_skipped)
    log.info("%s", "=" * LINE_LENGTH)
    
    sys.exit(0 if total_skipped == 0 else 1)

