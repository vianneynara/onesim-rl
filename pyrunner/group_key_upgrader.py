"""
Group Key Upgrader: Add cg@{group} token to existing run-id directories.

This module upgrades run-id directories from the old format (without group token) to the new format
that includes the config group (abbreviated as 'cg'). It scans existing run-id folders, matches them
to active configs in LIST_OF_CONFIGS by comparing algorithm, runs, and behavior policy, then renames
directories to insert the cg@{group} token.

Format transformation:
  Old: cfg@01-ql500-eg_ed@0.99
  New: cfg@01-cg@ql_epsilon-ql500-eg_ed@0.99

Supports both single parent-dir-id and batch operations with --all flag.

Usage:
  python pyrunner/group_key_upgrader.py --parent-dir-id ql-p-ms@0 --dry-run
  python pyrunner/group_key_upgrader.py --parent-dir-id "ql-p-ms@0,ql-p-ms@1" --dry-run
  python pyrunner/group_key_upgrader.py --all --dry-run
  python pyrunner/group_key_upgrader.py --parent-dir-id ql-c-ms@0
"""

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
from pyrunner.utils.path import normalize_report_base

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# REPORTS_BASE = r"reports/skripsi"
REPORTS_BASE = r"D:\Developments+\Java\onesim-rl-data\reports"

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
    Extract algorithm and runs from folder name like 'cfg@05-ql500-...' or 'cfg@05-cg@...-ql500-...'.
    Returns: (alg, runs) tuple or None if not found.
    """
    # Pattern: cfg@NN(-cg@...)? -ALG[digits]-...
    # First try new format with cg@
    match = re.search(r"(?:cfg@\d+-(?:cg@[^\-]+-)?)(\w+?)(\d+)", folder_name)
    if match:
        alg = match.group(1)
        try:
            runs = int(match.group(2))
            return alg, runs
        except ValueError:
            pass
    return None


def extract_behavior_policy(folder_name: str) -> Optional[str]:
    """
    Extract behavior policy from folder name by looking for patterns like:
    - qlm_bp@ucb (UCB)
    - qlm_bp@ts (Thompson Sampling)
    - qlm_bp@epsilon (Epsilon-Greedy)
    
    Returns: behavior policy name (e.g., 'ucb', 'ts', 'epsilon') or None if not found.
    """
    if re.search(r"cfg@\d+-ql\d+", folder_name):
        # Q-Learning algorithm
        match = re.search(r"qlm_bp@(\w+)", folder_name)
        if match:
            return match.group(1)
        # If no explicit qlm_bp@, it's epsilon-greedy (default)
        return "epsilon"
    
    # For Lévy Flight, there's no behavior policy
    if re.search(r"cfg@\d+-lfe\d+", folder_name):
        return None
    
    return None


def build_config_signature(alg: str, runs: int, bp: Optional[str] = None) -> str:
    """Build a signature string for matching configs."""
    sig = f"{alg}+{runs}"
    if bp:
        sig = f"{sig}+{bp}"
    return sig


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


def scan_run_id_folders(parent_dir_id: str, reports_base: str = REPORTS_BASE) -> Dict[int, str]:
    """
    Scan run-id directory and extract all cfg@N folders.
    
    Args:
        parent_dir_id: Parent directory identifier
        reports_base: Base reports directory path
    
    Returns: {cfg_index: folder_name, ...}
    Example: {1: 'cfg@01-ql500-eg_ed@0.99', 5: 'cfg@05-ql500-qlm_bp@ucb-ucb_ec@0.5'}
    """
    run_id_path = os.path.join(reports_base, parent_dir_id, "run-id")
    
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


def has_group_token(folder_name: str) -> bool:
    """Check if folder already has cg@ token (already upgraded)."""
    return "cg@" in folder_name


def build_upgrade_mapping(
        existing_folders: Dict[int, str],
        active_configs: Dict[int, dict]
) -> Tuple[Dict[str, str], List[str]]:
    """
    Build a mapping from old folder name to new folder name with group token inserted.
    
    Matches folders by (algorithm, runs, behavior_policy) signature and uses the group
    value from the matching active config.
    
    Returns: (rename_mapping, info_messages)
    - rename_mapping: {old_folder_name: new_folder_name, ...}
    - info_messages: list of log messages
    """
    rename_mapping = {}
    messages = []
    
    # Build signature -> group value mapping from active configs
    sig_to_group: Dict[str, str] = {}
    sig_to_first_idx: Dict[str, int] = {}
    
    for cfg_idx, config in active_configs.items():
        alg = config["alg"]
        runs = config["runs"]
        bp = config.get("bp")
        group = config.get("group")
        
        sig = build_config_signature(alg, runs, bp)
        sig_to_group[sig] = group
        
        if sig not in sig_to_first_idx:
            sig_to_first_idx[sig] = cfg_idx
    
    # Process existing folders
    for cfg_idx, old_folder_name in sorted(existing_folders.items()):
        # Check if already upgraded
        if has_group_token(old_folder_name):
            messages.append(f"cfg@{cfg_idx:02d}: Already has cg@ token, skipping")
            continue
        
        # Extract algorithm, runs, and behavior policy
        alg_runs = extract_alg_and_runs(old_folder_name)
        if not alg_runs:
            messages.append(f"cfg@{cfg_idx:02d}: Could not extract alg+runs from '{old_folder_name}'")
            continue
        
        alg, runs = alg_runs
        bp = extract_behavior_policy(old_folder_name)
        sig = build_config_signature(alg, runs, bp)
        
        if sig not in sig_to_group:
            messages.append(
                f"cfg@{cfg_idx:02d} (sig={sig}): No matching active config found"
            )
            continue
        
        group = sig_to_group[sig]
        if not group:
            messages.append(
                f"cfg@{cfg_idx:02d} (sig={sig}): Matching config has no group key"
            )
            continue
        
        # Build new folder name by inserting cg@{group} after cfg@NN
        new_folder_name = re.sub(
            r"^(cfg@\d+)-",
            f"\\1-cg@{group}-",
            old_folder_name
        )
        
        if new_folder_name != old_folder_name:
            rename_mapping[old_folder_name] = new_folder_name
            messages.append(
                f"cfg@{cfg_idx:02d}: '{old_folder_name}' → '{new_folder_name}' (sig={sig}, group={group})"
            )
        else:
            messages.append(f"cfg@{cfg_idx:02d}: No change needed")
    
    return rename_mapping, messages


def execute_renames(
        parent_dir_id: str,
        rename_mapping: Dict[str, str],
        reports_base: str = REPORTS_BASE,
        dry_run: bool = True
) -> Tuple[int, int, int]:
    """
    Execute the actual renames (or dry-run).
    
    Returns: (total, successes, failures)
    """
    run_id_path = os.path.join(reports_base, parent_dir_id, "run-id")
    
    total = len(rename_mapping)
    successes = 0
    failures = 0
    
    for old_name, new_name in rename_mapping.items():
        old_path = os.path.join(run_id_path, old_name)
        new_path = os.path.join(run_id_path, new_name)
        
        if not os.path.exists(old_path):
            log.warning(f"Source folder not found: {old_path}")
            failures += 1
            continue
        
        if os.path.exists(new_path):
            log.warning(f"Destination already exists: {new_path}")
            failures += 1
            continue
        
        if dry_run:
            log.info(f"[DRY-RUN] Would rename: {old_name} → {new_name}")
            successes += 1
        else:
            try:
                shutil.move(old_path, new_path)
                log.info(f"Renamed: {old_name} → {new_name}")
                successes += 1
            except Exception as e:
                log.error(f"Failed to rename '{old_name}': {e}")
                failures += 1
    
    return total, successes, failures


def process_parent_dir(
        parent_dir_id: str,
        reports_base: str = REPORTS_BASE,
        dry_run: bool = True
) -> Tuple[int, int, int]:
    """
    Process a single parent directory.
    
    Returns: (total_renames, successes, failures)
    """
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Processing: %s", parent_dir_id)
    log.info("%s", "=" * LINE_LENGTH)
    
    # Scan existing folders
    existing_folders = scan_run_id_folders(parent_dir_id, reports_base)
    if not existing_folders:
        log.warning("No run-id folders found for %s", parent_dir_id)
        return 0, 0, 0
    
    log.info("Found %d existing run-id folders", len(existing_folders))
    
    # Get active configs
    active_configs = get_active_configs_mapping()
    
    # Build upgrade mapping
    rename_mapping, info_messages = build_upgrade_mapping(existing_folders, active_configs)
    
    # Log mapping info
    for msg in info_messages:
        log.info("  %s", msg)
    
    if not rename_mapping:
        log.info("No folders need upgrading")
        return 0, 0, 0
    
    log.info("Will rename %d folder(s)", len(rename_mapping))
    
    # Execute renames
    total, successes, failures = execute_renames(
        parent_dir_id,
        rename_mapping,
        reports_base,
        dry_run
    )
    
    log.info(
        "Result: %d total, %d successful, %d failed",
        total, successes, failures
    )
    
    return total, successes, failures


def main():
    parser = argparse.ArgumentParser(
        description="Upgrade existing run-id directories to include config group token (cg@)"
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--all",
        action="store_true",
        help="Process all parent directories (scan for all run-id dirs)"
    )
    group.add_argument(
        "--parent-dir-id",
        type=str,
        help="Parent directory ID(s) to process (comma-separated)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be renamed without actually renaming"
    )
    
    parser.add_argument(
        "--reports-base",
        type=str,
        default=REPORTS_BASE,
        help=f"Base reports directory (default: {REPORTS_BASE})"
    )
    
    args = parser.parse_args()
    
    # Normalize report base
    normalized_report_base = normalize_report_base(args.reports_base)
    
    start_time = datetime.now()
    total_renames = 0
    total_successes = 0
    total_failures = 0
    
    if args.all:
        # Scan all directories
        report_path = os.path.join(normalized_report_base)
        if not os.path.isdir(report_path):
            log.error("Reports base directory not found: %s", report_path)
            sys.exit(1)
        
        parent_dirs = sorted([
            d for d in os.listdir(report_path)
            if os.path.isdir(os.path.join(report_path, d)) and os.path.isdir(os.path.join(report_path, d, "run-id"))
        ])
        
        if not parent_dirs:
            log.warning("No run-id directories found in %s", report_path)
            sys.exit(0)
        
        log.info("Found %d parent directories with run-id folders", len(parent_dirs))
        
        for parent_dir in parent_dirs:
            total, successes, failures = process_parent_dir(
                parent_dir,
                normalized_report_base,
                args.dry_run
            )
            total_renames += total
            total_successes += successes
            total_failures += failures
    
    else:
        # Process specified parent directories
        parent_dirs = [d.strip() for d in args.parent_dir_id.split(",")]
        
        for parent_dir in parent_dirs:
            total, successes, failures = process_parent_dir(
                parent_dir,
                normalized_report_base,
                args.dry_run
            )
            total_renames += total
            total_successes += successes
            total_failures += failures
    
    # Summary
    end_time = datetime.now()
    elapsed = end_time - start_time
    
    log.info("%s", "=" * LINE_LENGTH)
    log.info("[SUMMARY] Upgrade completed in %s", elapsed)
    log.info(
        "Total: %d renames, %d successful, %d failed",
        total_renames, total_successes, total_failures
    )
    
    if args.dry_run:
        log.info("This was a DRY-RUN. To actually rename, remove --dry-run flag.")
    
    log.info("%s", "=" * LINE_LENGTH)


if __name__ == "__main__":
    main()


