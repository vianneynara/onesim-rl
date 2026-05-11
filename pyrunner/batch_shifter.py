"""
Batch Shifter: Automatically rename cfg@N prefixed run-id folders when batch configs are reordered/commented.

This module renames existing run-id folders to match the current active configs in LIST_OF_CONFIGS,
accounting for changes created by commented-out/deleted configs (downward shifts) or new configs added (upward shifts).

Supports both shift directions:
  - DOWNWARD shift (configs removed): cfg@5 becomes cfg@3, cfg@6 becomes cfg@4
  - UPWARD shift (configs added): cfg@2 becomes cfg@3, cfg@3 becomes cfg@4

Smart matching groups configs by signature (alg+runs+behavior_policy) and matches by relative position within groups,
enabling accurate remapping regardless of shift direction.

Usage:
  python pyrunner/batch_shifter.py --parent-dir-id ql-p-ms@0 --dry-run
  python pyrunner/batch_shifter.py --parent-dir-id "ql-p-ms@0,ql-p-ms@1" --dry-run
  python pyrunner/batch_shifter.py --all --dry-run
  python pyrunner/batch_shifter.py --all
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


def extract_behavior_policy(folder_name: str) -> Optional[str]:
    """
    Extract behavior policy from folder name by looking for patterns like:
    - qlm_bp@ucb (UCB)
    - qlm_bp@ts (Thompson Sampling)
    - qlm_bp@epsilon (not typically used, but possible)
    - absence of qlm_bp@ indicates epsilon-greedy (default for QL)
    
    Returns: behavior policy name (e.g., 'ucb', 'ts', 'epsilon') or None if not found.
    Example: 'cfg@11-ql500-qlm_bp@ucb-ucb_ec@0.5' → 'ucb'
    """
    # Look for qlm_bp@<value> or mcm_bp@<value>
    match = re.search(r"(?:qlm_bp|mcm_bp)@(\w+)", folder_name)
    if match:
        return match.group(1)
    
    # If no behavior policy marker found, it's likely epsilon-greedy (default for QL)
    # Check if it's a QL config by looking for ql in the name
    if re.search(r"cfg@\d+-ql\d+", folder_name):
        return "epsilon"
    
    return None


def build_config_signature(alg: str, runs: int, bp: Optional[str] = None) -> str:
    """
    Build a signature from algorithm, runs, and optional behavior policy.
    
    This ensures configs with different behavior policies are matched separately.
    
    Examples:
      - ql500+epsilon (epsilon-greedy)
      - ql500+ucb (UCB exploration)
      - ql500+ts (Thompson Sampling)
      - lfe500 (no behavior policy)
    
    Returns: signature string
    """
    sig = f"{alg}{runs}"
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
    
    Smart matching that handles both UPWARD and DOWNWARD shifts by grouping
    configs by signature (alg+runs+behavior_policy) and matching by relative position:
    
    - Downward shift: configs removed → cfg@5 → cfg@3
    - Upward shift: configs added → cfg@2 → cfg@3
    
    Example:
      Before: existing folders at indices [31, 32] (both QL Thompson Sampling)
      After: active QL Thompson Sampling at [23, 24, 25, 26, 27]
      Result: cfg@31 → 23, cfg@32 → 24 (matches by position, groups by alg+runs+bp)
    
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
    
    # Build signature → indices mapping for active configs
    # Groups configs by their algorithm+runs+behavior_policy signature
    active_sig_to_indices = {}
    for idx in active_indices:
        config = active_configs[idx]
        alg = config["alg"]
        runs = config["runs"]
        bp = config.get("bp")  # Extract behavior policy from config (epsilon, ucb, ts, or None)
        sig = build_config_signature(alg, runs, bp)
        if sig not in active_sig_to_indices:
            active_sig_to_indices[sig] = []
        active_sig_to_indices[sig].append(idx)
    
    log.info("Active signature groups: %s", {sig: len(idxs) for sig, idxs in active_sig_to_indices.items()})
    
    # Build signature → indices mapping for existing folders
    existing_sig_to_indices = {}
    for old_idx in existing_indices:
        folder_name = existing_folders[old_idx]
        alg_runs_sig = extract_alg_and_runs(folder_name)
        
        if alg_runs_sig is None:
            problems.append(f"Could not extract alg+runs from folder: {folder_name}")
            continue
        
        alg, runs = alg_runs_sig
        bp = extract_behavior_policy(folder_name)  # Extract behavior policy from folder name
        sig = build_config_signature(alg, runs, bp)
        
        if sig not in existing_sig_to_indices:
            existing_sig_to_indices[sig] = []
        existing_sig_to_indices[sig].append(old_idx)
    
    log.info("Existing signature groups: %s", {sig: len(idxs) for sig, idxs in existing_sig_to_indices.items()})
    
    # Match existing folders to active configs by signature group
    # Within each group, match by relative position (order-preserving)
    # This works for both UPWARD shifts (adding configs) and DOWNWARD shifts (removing configs)
    matched_active = set()
    
    for sig in sorted(existing_sig_to_indices.keys()):
        existing_idx_list = sorted(existing_sig_to_indices[sig])
        
        if sig not in active_sig_to_indices:
            for old_idx in existing_idx_list:
                problems.append(
                    f"No matching active config for existing index {old_idx} (signature={sig}). "
                    f"This algorithm/runs/policy combination is no longer in the active configs."
                )
            continue
        
        active_idx_list = sorted(active_sig_to_indices[sig])
        
        # Get unmatched active indices for this signature
        unmatched_active = [idx for idx in active_idx_list if idx not in matched_active]
        
        log.info("Signature group '%s': %d existing, %d active unmatched", sig, len(existing_idx_list), len(unmatched_active))
        
        if len(existing_idx_list) > len(unmatched_active):
            problems.append(
                f"Signature {sig}: {len(existing_idx_list)} existing folders but only "
                f"{len(unmatched_active)} available active configs. Cannot match all folders."
            )
        
        # First pass: Try to match by override parameters (more precise)
        matched_by_params = {}
        unmatched_existing = []
        
        for old_idx in existing_idx_list:
            folder_name = existing_folders[old_idx]
            folder_params = extract_override_params(folder_name)
            
            log.debug("  Checking old_idx %d: folder_params=%s", old_idx, folder_params)
            
            if not folder_params:
                # No override params in folder, defer to position matching
                unmatched_existing.append(old_idx)
                continue
            
            # Try to find an active config with matching params
            found_match = False
            for new_idx in unmatched_active:
                if new_idx in matched_active:
                    continue
                
                active_config = active_configs[new_idx]
                config_params = config_to_override_params(active_config)
                
                log.debug("    Comparing with new_idx %d: config_params=%s", new_idx, config_params)
                
                # Check if params match
                if folder_params == config_params:
                    matched_by_params[old_idx] = new_idx
                    matched_active.add(new_idx)
                    found_match = True
                    log.info("  Matched: cfg@%02d → cfg@%02d (signature=%s, override params match)", old_idx, new_idx, sig)
                    break
            
            if not found_match:
                unmatched_existing.append(old_idx)
                log.debug("    No param match found for old_idx %d", old_idx)

        # Second pass: Match remaining by position
        unmatched_active_filtered = [idx for idx in unmatched_active if idx not in matched_active]
        
        for i, old_idx in enumerate(unmatched_existing):
            if i < len(unmatched_active_filtered):
                new_idx = unmatched_active_filtered[i]
                rename_mapping[old_idx] = new_idx
                matched_active.add(new_idx)
                log.info("  Matched: cfg@%02d → cfg@%02d (signature=%s, position=%d)", old_idx, new_idx, sig, i)
            else:
                problems.append(
                    f"No available active config for existing index {old_idx} (signature={sig}). "
                    f"Cannot match this folder ({len(existing_idx_list)} total needed, only {len(unmatched_active)} available)."
                )
        
        # Add param-matched mappings to the final mapping
        rename_mapping.update(matched_by_params)
    
    return rename_mapping, problems


def move_to_archive(src_path: str, archive_base: str) -> Tuple[bool, str]:
    """
    Move a folder to the _shifted archive directory.
    
    Preserves the folder name as-is (does not rename).
    
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
        # Use shutil.copytree to copy (not move) for backup purposes
        # This way we keep the original renamed folder in reports/skripsi/
        import shutil
        shutil.copytree(src_path, dst_path)
        return True, f"Backed up to {dst_path}"
    except Exception as e:
        return False, f"Failed to backup {src_path}: {e}"


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
                log.info("  (would archive old to: %s)", os.path.join(REPORTS_SHIFTED, parent_dir_id, "run-id", old_folder_name))
            renamed_count += 1
        else:
            # Step 1: Rename folder in-place in reports/skripsi/
            ok, msg = rename_folder(old_path, old_folder_name, new_folder_name)
            if not ok:
                log.error("RENAME FAILED: %s", msg)
                skipped_count += 1
                continue
            
            log.info("RENAMED: %s", msg)
            
            # Step 2: Optionally archive old folder name as backup
            if not no_archive:
                ok, msg = move_to_archive(new_path, REPORTS_SHIFTED)
                if ok:
                    log.info("ARCHIVED BACKUP: %s (to %s)", new_folder_name, msg)
                else:
                    log.warning("ARCHIVE BACKUP FAILED: %s (but rename succeeded, so continuing)", msg)
            
            renamed_count += 1
    
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


def extract_override_params(folder_name: str) -> Dict[str, str]:
    """
    Extract override parameters from folder name.
    
    Looks for patterns like:
    - ts_iv@5.0
    - ucb_ec@2.5
    - eg_ed@0.99
    - lfe_la@1.5
    
    Returns: {param_key: param_value, ...}
    Example: 'cfg@31-ql500-qlm_bp@ts-ts_iv@5.0' → {'ts_iv': '5.0'}
    """
    params = {}
    # Match patterns like key@value
    matches = re.findall(r"(\w+)@([\d.]+)", folder_name)
    for key, value in matches:
        # Skip behavior policy keys (qlm_bp, mcm_bp) and cfg@ index as those are handled separately
        if key not in ("qlm_bp", "mcm_bp", "cfg"):
            params[key] = value
    return params


def config_to_override_params(config: dict) -> Dict[str, str]:
    """
    Convert config overrides dict to comparable format.
    
    Takes overrides from config and converts numeric values to strings for comparison.
    
    Returns: {param_key: param_value_as_string, ...}
    """
    params = {}
    overrides = config.get("overrides", {})
    if overrides:
        for key, value in overrides.items():
            params[key] = str(value)
    return params



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

