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
import hashlib
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

# from pyrunner.batch_configs import LIST_OF_CONFIGS
from pyrunner.batch_configs_jord import LIST_OF_CONFIGS

from pyrunner.utils.path import normalize_report_base

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
REPORTS_ORPHANED = "reports/_orphaned"


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

    Supports two patterns:
      - Standard:  cfg@NN-ALG[digits]-...           e.g. cfg@01-mcn500-...
      - With cg@:  cfg@NN-cg@STR-ALG[digits]-...   e.g. cfg@01-cg@foo-mcn500-...
    """
    # Fallback pattern: cfg@NN-cg@STR-ALG[digits]-...
    match = re.match(r"cfg@\d+-cg@(\w+)-(\w+?)(\d+)", folder_name)
    if match:
        alg = match.group(2)
        try:
            runs = int(match.group(3))
            return alg, runs
        except ValueError:
            pass

    # Standard pattern: cfg@NN-ALG[digits]-...
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
    - qlm_bp@ucb  / mcnm_bp@ucb   (UCB)
    - qlm_bp@ts   / mcnm_bp@ts    (Thompson Sampling)
    - qlm_bp@epsilon / mcnm_bp@epsilon
    - absence of *m_bp@ on a QL or MCN folder → epsilon-greedy (default)

    Returns: behavior policy name (e.g., 'ucb', 'ts', 'epsilon') or None if not found.
    Example: 'cfg@11-mcn500-mcnm_bp@ucb-ucb_ec@0.5' → 'ucb'
    """
    # Look for qlm_bp@<value>, mcm_bp@<value>, or mcnm_bp@<value>
    match = re.search(r"(?:qlm_bp|mcm_bp|mcnm_bp)@(\w+)", folder_name)
    if match:
        return match.group(1)

    # If no behavior policy marker found, it's likely epsilon-greedy (default)
    # Check if it's a QL or MCN config by looking for alg prefix in the name
    if re.search(r"cfg@\d+-(?:ql|mcn)\d+", folder_name):
        return "epsilon"

    return None


def build_config_signature(alg: str, runs: int, bp: Optional[str] = None) -> str:
    """
    Build a signature from algorithm, runs, and optional behavior policy.

    This ensures configs with different behavior policies are matched separately.

    Examples:
      - mcn500+epsilon (epsilon-greedy)
      - mcn500+ucb     (UCB exploration)
      - mcn500+ts      (Thompson Sampling)
      - ql500+epsilon
      - lfe500         (no behavior policy)

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


def scan_run_id_folders(parent_dir_id: str, reports_base: str = REPORTS_BASE) -> Dict[int, List[Tuple[str, float]]]:
    """
    Scan run-id directory and extract all cfg@N folders with their modification times.

    Returns Dict[int, List[Tuple[str, float]]] — a list of (folder_name, mtime) per index,
    so that multiple folders sharing the same cfg@ index are each captured (duplicate-index fix),
    and modification time is available for tiebreaking when params are identical.

    Args:
        parent_dir_id: Parent directory identifier
        reports_base: Base reports directory path

    Returns: {cfg_index: [(folder_name, mtime), ...], ...}
    Example: {1: [('cfg@01-mcn500-...', 1716123456.0)], 11: [('cfg@11-mcn500-...', 1716123789.0)]}
    """
    run_id_path = os.path.join(reports_base, parent_dir_id, "run-id")

    if not os.path.isdir(run_id_path):
        log.warning("Run-id directory not found: %s", run_id_path)
        return {}

    cfg_folders: Dict[int, List[Tuple[str, float]]] = {}
    for folder_name in os.listdir(run_id_path):
        folder_path = os.path.join(run_id_path, folder_name)
        if not os.path.isdir(folder_path):
            continue

        cfg_idx = extract_cfg_index(folder_name)
        if cfg_idx is not None:
            mtime = os.path.getmtime(folder_path)
            if cfg_idx not in cfg_folders:
                cfg_folders[cfg_idx] = []
            cfg_folders[cfg_idx].append((folder_name, mtime))

    return cfg_folders


def extract_override_params(folder_name: str) -> Dict[str, str]:
    """
    Extract override parameters from folder name.

    Looks for patterns like:
    - ts_iv@5.0
    - ucb_ec@2.5
    - eg_ed@0.99
    - lfe_la@1.5
    - mcnm_fv@True / mcnm_fv@False
    - ucb_reset@True
    - ts_bayesian@True / ts_reset@False

    Returns: {param_key: param_value, ...}
    Example: 'cfg@14-mcn500-mcnm_bp@ts-ts_bayesian@True-ts_reset@True-mcnm_fv@True'
             → {'ts_bayesian': 'True', 'ts_reset': 'True', 'mcnm_fv': 'True'}
    """
    params = {}
    # Match patterns like key@value — numeric OR boolean
    matches = re.findall(r"(\w+)@([\d.]+|True|False)", folder_name)
    for key, value in matches:
        # Skip behavior policy keys and the cfg@ index — handled separately
        if key not in ("qlm_bp", "mcm_bp", "mcnm_bp", "cfg"):
            params[key] = value
    return params


def config_to_override_params(config: dict) -> Dict[str, str]:
    """
    Convert config overrides dict to comparable format.

    Converts all values to strings for comparison against folder-extracted params.
    Booleans are rendered as 'True'/'False' to match folder name conventions
    (Python's str(True) == 'True' already, but this is made explicit here).

    Returns: {param_key: param_value_as_string, ...}
    """
    params = {}
    overrides = config.get("overrides", {})
    for key, value in overrides.items():
        if isinstance(value, bool):
            params[key] = str(value)   # True → 'True', False → 'False'
        else:
            params[key] = str(value)
    return params


def build_rename_mapping(
        existing_folders_dict: Dict[int, List[Tuple[str, float]]],
        active_configs: Dict[int, dict],
        index_only: bool = False
) -> Tuple[Dict[str, Tuple[int, int]], List[str]]:
    """
    Build a mapping from existing folder name → (new_cfg_index, sub_index).

    Keys are folder names (not old indices) so that multiple folders sharing
    the same cfg@ index are each mapped correctly (duplicate-index bug fix).

    When multiple existing folders map to the same new cfg index (identical params),
    they are sorted by modification time (oldest first) and receive sub-indices:
      sub_index = 0  →  cfg@NN          (oldest / no suffix)
      sub_index = 1  →  cfg@NN-1        (second oldest)
      sub_index = 2  →  cfg@NN-2        (third oldest)
      etc.

    Smart matching groups configs by signature (alg+runs+behavior_policy) and
    matches first by override parameter equality, then by relative position.

    Returns: (rename_mapping, problems)
    - rename_mapping: {folder_name: (new_index, sub_index), ...}
    - problems: list of warning/info messages
    """
    rename_mapping: Dict[str, Tuple[int, int]] = {}
    problems: List[str] = []

    active_indices = sorted(active_configs.keys())

    # Flatten existing_folders_dict into a list of (old_idx, folder_name, mtime) triples
    all_existing_folders: List[Tuple[int, str, float]] = []
    for idx, items in existing_folders_dict.items():
        for fname, mtime in items:
            all_existing_folders.append((idx, fname, mtime))

    existing_indices = sorted(existing_folders_dict.keys())
    log.info("Active config indices: %s", active_indices)
    log.info("Existing folder indices: %s", existing_indices)

    # Build signature → active config indices mapping
    active_sig_to_indices: Dict[str, List[int]] = {}
    for idx in active_indices:
        config = active_configs[idx]
        alg = config["alg"]
        runs = config["runs"]
        bp = config.get("bp")
        sig = build_config_signature(alg, runs, bp)
        if sig not in active_sig_to_indices:
            active_sig_to_indices[sig] = []
        active_sig_to_indices[sig].append(idx)

    log.info("Active signature groups: %s", {sig: len(idxs) for sig, idxs in active_sig_to_indices.items()})

    # Build signature → (old_idx, folder_name, mtime) list mapping
    existing_sig_to_folders: Dict[str, List[Tuple[int, str, float]]] = {}
    for old_idx, folder_name, mtime in all_existing_folders:
        alg_runs = extract_alg_and_runs(folder_name)
        if alg_runs is None:
            problems.append(f"Could not extract alg+runs from folder: {folder_name}")
            continue

        alg, runs = alg_runs
        bp = extract_behavior_policy(folder_name)
        sig = build_config_signature(alg, runs, bp)

        if sig not in existing_sig_to_folders:
            existing_sig_to_folders[sig] = []
        existing_sig_to_folders[sig].append((old_idx, folder_name, mtime))

    log.info("Existing signature groups: %s", {sig: len(items) for sig, items in existing_sig_to_folders.items()})

    matched_active: set = set()

    # Track how many folders have been assigned to each new_idx so far,
    # to generate sub-indices for duplicates: 0 = no suffix, 1 = -1, 2 = -2, ...
    # Within the same new_idx, folders are ordered oldest→newest (mtime ascending),
    # so the oldest run gets the clean cfg@N name and newer duplicates get cfg@N-1, cfg@N-2.
    new_idx_counts: Dict[int, int] = {}

    for sig in sorted(existing_sig_to_folders.keys()):
        # Sort by (old_idx, folder_name) for deterministic ordering across different params.
        # mtime tiebreaking is applied later within identical-param groups.
        existing_item_list = sorted(existing_sig_to_folders[sig], key=lambda x: (x[0], x[1]))
        active_idx_list = sorted(active_sig_to_indices.get(sig, []))

        if not active_idx_list:
            for old_idx, folder_name, mtime in existing_item_list:
                problems.append(
                    f"No matching active config for folder {folder_name} (signature={sig}). "
                    f"This algorithm/runs/policy combination is no longer in the active configs."
                )
            continue

        unmatched_active = [idx for idx in active_idx_list if idx not in matched_active]

        log.info(
            "Signature group '%s': %d existing, %d active unmatched",
            sig, len(existing_item_list), len(unmatched_active)
        )

        if len(existing_item_list) > len(unmatched_active):
            problems.append(
                f"Signature {sig}: {len(existing_item_list)} existing folders but only "
                f"{len(unmatched_active)} available active configs. Cannot match all folders."
            )

        # Pass 1: Group folders by their override params, then sort each param-group
        # by mtime (oldest first). This ensures that when two folders share identical
        # params and map to the same new_idx, the oldest gets sub_idx=0 (no suffix)
        # and newer ones get sub_idx=1, sub_idx=2, etc.
        from collections import defaultdict
        param_groups: Dict[str, List[Tuple[int, str, float]]] = defaultdict(list)
        no_param_folders: List[Tuple[int, str, float]] = []

        for old_idx, folder_name, mtime in existing_item_list:
            fp = extract_override_params(folder_name)
            if fp:
                param_key = str(sorted(fp.items()))
                param_groups[param_key].append((old_idx, folder_name, mtime))
            else:
                no_param_folders.append((old_idx, folder_name, mtime))

        # Sort each param group by mtime ascending (oldest first)
        for key in param_groups:
            param_groups[key].sort(key=lambda x: x[2])

        # Rebuild existing_item_list: param-groups first (sorted by mtime within group),
        # then no-param folders, maintaining overall (old_idx, name) ordering between groups
        matched_by_params: Dict[str, Tuple[int, int]] = {}
        unmatched_existing: List[Tuple[int, str, float]] = []

        processed_param_keys = set()
        for old_idx, folder_name, mtime in existing_item_list:
            fp = extract_override_params(folder_name)
            if fp:
                param_key = str(sorted(fp.items()))
                if param_key in processed_param_keys:
                    continue  # already handled this group
                processed_param_keys.add(param_key)

                group = param_groups[param_key]  # already sorted oldest→newest
                # Find a matching active config for this param set
                matching_new_idx = None
                for new_idx in unmatched_active:
                    if new_idx in matched_active:
                        continue
                    if fp == config_to_override_params(active_configs[new_idx]):
                        matching_new_idx = new_idx
                        break

                if matching_new_idx is not None:
                    matched_active.add(matching_new_idx)
                    for rank, (g_old_idx, g_folder_name, g_mtime) in enumerate(group):
                        sub_idx = new_idx_counts.get(matching_new_idx, 0)
                        new_idx_counts[matching_new_idx] = sub_idx + 1
                        matched_by_params[g_folder_name] = (matching_new_idx, sub_idx)
                        from datetime import datetime as dt
                        mtime_str = dt.fromtimestamp(g_mtime).strftime("%Y-%m-%d %H:%M:%S")
                        log.info(
                            "  Matched (params): %s → cfg@%02d%s (signature=%s, mtime=%s%s)",
                            g_folder_name, matching_new_idx,
                            f"-{sub_idx}" if sub_idx > 0 else "",
                            sig, mtime_str,
                            " [oldest=primary]" if rank == 0 and len(group) > 1 else
                            f" [duplicate #{rank}, newer]" if len(group) > 1 else ""
                        )
                else:
                    for g_old_idx, g_folder_name, g_mtime in group:
                        unmatched_existing.append((g_old_idx, g_folder_name, g_mtime))
            else:
                unmatched_existing.append((old_idx, folder_name, mtime))

        # Pass 2: Match remaining by relative position within the signature group
        unmatched_active_filtered = [idx for idx in unmatched_active if idx not in matched_active]

        for i, (old_idx, folder_name, mtime) in enumerate(unmatched_existing):
            folder_params = extract_override_params(folder_name)

            if folder_params:
                param_exists = any(
                    folder_params == config_to_override_params(active_configs[aidx])
                    for aidx in active_idx_list
                )
                if not param_exists:
                    log.info(
                        "  Skipping position match for %s (signature=%s): "
                        "params %s don't exist in any active config",
                        folder_name, sig, folder_params
                    )
                    problems.append(
                        f"Folder {folder_name} (signature={sig}, params={folder_params}) "
                        f"has no matching active config. Will be archived as orphaned."
                    )
                    continue

            if i < len(unmatched_active_filtered):
                new_idx = unmatched_active_filtered[i]
                sub_idx = new_idx_counts.get(new_idx, 0)
                new_idx_counts[new_idx] = sub_idx + 1
                rename_mapping[folder_name] = (new_idx, sub_idx)
                matched_active.add(new_idx)
                log.info(
                    "  Matched (position %d): %s → cfg@%02d%s (signature=%s)",
                    i, folder_name, new_idx,
                    f"-{sub_idx}" if sub_idx > 0 else "",
                    sig
                )
            else:
                problems.append(
                    f"No available active config for folder {folder_name} (signature={sig}). "
                    f"Cannot match ({len(existing_item_list)} needed, only {len(unmatched_active)} available)."
                )

        # Merge param-matched entries into final mapping
        rename_mapping.update(matched_by_params)

    return rename_mapping, problems


def move_to_archive(src_path: str, archive_base: str, parent_dir_id: str, folder_name: str) -> Tuple[bool, str]:
    """
    Copy a folder into the archive directory (backup semantics — original stays).

    Preserves the folder name as-is (does not rename).

    Args:
        src_path:      Full path to the source folder
        archive_base:  Base archive directory (e.g. reports/_orphaned)
        parent_dir_id: Parent directory identifier (e.g. test-shifter)
        folder_name:   Folder name only (e.g. cfg@05-mcn500-...)

    Returns: (success, message)
    """
    if not os.path.isdir(src_path):
        return False, f"Source path not found: {src_path}"

    archive_path = os.path.join(archive_base, parent_dir_id, "run-id")
    os.makedirs(archive_path, exist_ok=True)

    dst_path = os.path.join(archive_path, folder_name)

    if os.path.exists(dst_path):
        return False, f"Archive destination already exists: {dst_path}"

    try:
        shutil.copytree(src_path, dst_path)
        return True, f"Backed up to {dst_path}"
    except Exception as e:
        return False, f"Failed to backup {src_path}: {e}"


def rename_folder(old_path: str, old_name: str, new_name: str) -> Tuple[bool, str]:
    """Rename a folder from old_name to new_name in-place."""
    new_path = os.path.join(os.path.dirname(old_path), new_name)

    if os.path.exists(new_path):
        return False, f"Destination already exists: {new_path}"

    try:
        os.rename(old_path, new_path)
        return True, f"Renamed {old_name} → {new_name}"
    except Exception as e:
        return False, f"Failed to rename: {e}"


def generate_folder_hash(folder_path: str) -> str:
    """
    Generate an 8-character MD5 hash for a folder path.
    Used as a temporary suffix during two-pass rename to prevent collisions.

    Returns: 8-character hex string
    """
    return hashlib.md5(folder_path.encode()).hexdigest()[:8]


def rename_with_temp_hash(old_path: str, old_name: str, temp_hash: str) -> Tuple[bool, str]:
    """
    Rename a folder by inserting a temporary hash after the cfg@NN prefix.

    Pass 1: cfg@05-mcn500-... → cfg@05-a1b2c3d4-mcn500-...

    Returns: (success, new_name_or_error_msg)
    """
    match = re.match(r"(cfg@\d+)", old_name)
    if not match:
        return False, f"Invalid folder name format (no cfg@N prefix): {old_name}"

    cfg_prefix = match.group(1)
    rest = old_name[len(cfg_prefix):]   # Everything after cfg@NN

    new_name = f"{cfg_prefix}-{temp_hash}{rest}"
    new_path = os.path.join(os.path.dirname(old_path), new_name)

    if os.path.exists(new_path):
        return False, f"Hash temp destination already exists: {new_path}"

    try:
        os.rename(old_path, new_path)
        return True, new_name
    except Exception as e:
        return False, f"Failed to rename with temp hash: {e}"


def rename_from_temp_hash(old_path: str, old_name: str, new_cfg_index: int, sub_idx: int, temp_hash: str) -> Tuple[bool, str]:
    """
    Rename a temporary hash-suffixed folder to its final name.

    Pass 2: cfg@05-a1b2c3d4-mcn500-... → cfg@03-mcn500-...      (sub_idx=0)
            cfg@05-a1b2c3d4-mcn500-... → cfg@03-1-mcn500-...    (sub_idx=1)

    Returns: (success, new_name_or_error_msg)
    """
    pattern = rf"^(cfg@\d+)-{re.escape(temp_hash)}(.*)$"
    match = re.match(pattern, old_name)

    if not match:
        return False, f"Invalid temp hash folder format: {old_name}"

    rest = match.group(2)   # Everything after the hash
    new_prefix = f"cfg@{new_cfg_index:02d}" if sub_idx == 0 else f"cfg@{new_cfg_index:02d}-{sub_idx}"
    new_name = f"{new_prefix}{rest}"
    new_path = os.path.join(os.path.dirname(old_path), new_name)

    if os.path.exists(new_path):
        return False, f"Destination already exists: {new_path}"

    try:
        os.rename(old_path, new_path)
        return True, new_name
    except Exception as e:
        return False, f"Failed to rename from temp hash: {e}"


def execute_shift(
        parent_dir_id: str,
        reports_base: str = REPORTS_BASE,
        index_only: bool = False,
        dry_run: bool = False,
        no_archive: bool = False,
        force: bool = False
) -> Tuple[int, int]:
    """
    Execute the shift operation for a specific parent_dir_id.

    Handles three types of folders:
    1. Mapped folders:   Renamed from old index to new index
    2. Orphaned folders: Exist but don't match any active config → moved to _orphaned
    3. Skipped folders:  No change needed (old_idx == new_idx)

    Orphaned folders are ALWAYS moved to reports/_orphaned regardless of --no-archive flag
    (they represent obsolete runs that no longer match the batch_configs).

    Returns: (renamed_count, skipped_count)
    """
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Processing parent_dir_id: %s", parent_dir_id)
    log.info("=" * LINE_LENGTH)

    pid_path = os.path.join(reports_base, parent_dir_id)
    if not os.path.isdir(pid_path):
        log.warning("Parent dir not found: %s", pid_path)
        return 0, 0

    active_configs = get_active_configs_mapping()
    existing_folders_dict = scan_run_id_folders(parent_dir_id, reports_base)

    if not existing_folders_dict:
        log.warning("No cfg@N folders found in %s", parent_dir_id)
        return 0, 0

    rename_mapping, problems = build_rename_mapping(existing_folders_dict, active_configs, index_only)

    if problems:
        log.warning("Mapping notifications:")
        for p in problems:
            log.warning("  - %s", p)

    renamed_count   = 0
    skipped_count   = 0
    orphaned_count  = 0
    duplicate_count = 0

    # Flatten all (folder_name, mtime) tuples for orphan detection and duplicate reporting
    all_folder_names = [fname for items in existing_folders_dict.values() for fname, mtime in items]
    orphaned_folders = [f for f in all_folder_names if f not in rename_mapping]

    # ===== REPORT DUPLICATE INDICES =====
    duplicates = {idx: items for idx, items in existing_folders_dict.items() if len(items) > 1}
    if duplicates:
        total_dupes = sum(len(v) for v in duplicates.values()) - len(duplicates)
        log.info("Found %d index(es) with duplicate folders (%d extra folder(s) total):", len(duplicates), total_dupes)
        for idx in sorted(duplicates):
            log.info("  cfg@%02d has %d folders:", idx, len(duplicates[idx]))
            for fname, mtime in sorted(duplicates[idx], key=lambda x: x[1]):
                from datetime import datetime as dt
                mtime_str = dt.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                log.info("    - %s  (mtime: %s)", fname, mtime_str)

    # Build a set of folder names that are duplicates (sub_idx > 0) so we know
    # which renamed folders to copy into _duplicate after renaming.
    duplicate_folder_originals: set = {
        old_name for old_name, (new_idx, sub_idx) in rename_mapping.items() if sub_idx > 0
    }

    # ===== HANDLE ORPHANED FOLDERS =====
    # Folders that exist on disk but have no matching active config.
    # Always archived to _orphaned (even without --no-archive), to prevent future index clashes.
    if orphaned_folders:
        log.warning("Found %d orphaned folder(s) with no matching active configs:", len(orphaned_folders))
        for folder_name in sorted(orphaned_folders):
            log.warning(
                "  - %s (will be archived to %s to prevent future clashes)",
                folder_name, REPORTS_ORPHANED
            )

        if dry_run:
            log.info("DRY RUN: Would archive %d orphaned folder(s) to %s", len(orphaned_folders), REPORTS_ORPHANED)
            orphaned_count = len(orphaned_folders)
        else:
            for folder_name in sorted(orphaned_folders):
                src = os.path.join(reports_base, parent_dir_id, "run-id", folder_name)
                ok, msg = move_to_archive(src, REPORTS_ORPHANED, parent_dir_id, folder_name)
                if ok:
                    log.info("ARCHIVED ORPHANED: %s → %s", folder_name, msg)
                    try:
                        shutil.rmtree(src)
                        log.info("REMOVED ORPHANED: %s from original location", folder_name)
                        orphaned_count += 1
                    except Exception as e:
                        log.error("FAILED to remove orphaned %s: %s", folder_name, e)
                else:
                    log.error("FAILED to archive orphaned %s: %s", folder_name, msg)

    if not rename_mapping:
        log.warning("No renames needed (or no valid mappings found)")
        return 0, len(all_folder_names)

    def build_new_folder_name(old_folder_name: str, new_idx: int, sub_idx: int) -> str:
        """Replace cfg@NN in folder name with cfg@NN (sub_idx=0) or cfg@NN-K (sub_idx>0)."""
        new_prefix = f"cfg@{new_idx:02d}" if sub_idx == 0 else f"cfg@{new_idx:02d}-{sub_idx}"
        return re.sub(r"cfg@\d+", new_prefix, old_folder_name, count=1)

    # ===== DRY RUN: just log what would happen =====
    if dry_run:
        for old_folder_name, (new_idx, sub_idx) in rename_mapping.items():
            old_idx = extract_cfg_index(old_folder_name)
            new_folder_name = build_new_folder_name(old_folder_name, new_idx, sub_idx)
            if old_folder_name == new_folder_name:
                log.info("✓ Index %02d: No change needed (%s)", old_idx, old_folder_name)
                skipped_count += 1
            else:
                log.info("DRY RUN: %s → %s", old_folder_name, new_folder_name)
                if sub_idx > 0:
                    log.info(
                        "  (would move duplicate to: %s)",
                        os.path.join(reports_base, parent_dir_id, "_duplicate", new_folder_name)
                    )
                elif not no_archive and not force:
                    log.info(
                        "  (would archive old to: %s)",
                        os.path.join(REPORTS_SHIFTED, parent_dir_id, "run-id", old_folder_name)
                    )
                renamed_count += 1

    else:
        # ===== LIVE RENAME: Always two-pass with temp hashing =====
        # Two-pass is always used (not just --force) to prevent collisions where a
        # folder being renamed INTO already exists on disk under its new name.
        # E.g. cfg@01-...-eg_ed@0.99999 → cfg@11, but cfg@11-...-eg_ed@0.99999 already exists.
        # Pass 1 moves everything out of the way first, Pass 2 lands them at final names.
        log.info("Executing two-pass rename to prevent index collisions...")

        # Pass 1: cfg@NN-rest → cfg@NN-HASH-rest  (get everything out of the way)
        temp_hashes: Dict[str, Tuple[int, int, str]] = {}  # hashed_name → (new_idx, sub_idx, temp_hash)
        skipped_in_place: List[str] = []  # folder names that need no rename

        for old_folder_name, (new_idx, sub_idx) in rename_mapping.items():
            new_folder_name = build_new_folder_name(old_folder_name, new_idx, sub_idx)

            if old_folder_name == new_folder_name:
                skipped_in_place.append(old_folder_name)
                continue

            old_path = os.path.join(reports_base, parent_dir_id, "run-id", old_folder_name)
            temp_hash = generate_folder_hash(old_path)
            ok, hashed_name = rename_with_temp_hash(old_path, old_folder_name, temp_hash)
            if ok:
                temp_hashes[hashed_name] = (new_idx, sub_idx, temp_hash)
                log.info("PASS 1 (stage): %s → %s", old_folder_name, hashed_name)
            else:
                log.error("PASS 1 FAILED (stage): %s", hashed_name)
                skipped_count += 1

        # Log no-change folders
        for fname in skipped_in_place:
            old_idx = extract_cfg_index(fname)
            log.info("✓ Index %02d: No change needed (%s)", old_idx, fname)
            skipped_count += 1

        # Pass 2: cfg@NN-HASH-rest → cfg@MM[-K]-rest  (land at final names)
        for hashed_name, (new_idx, sub_idx, temp_hash) in temp_hashes.items():
            hashed_path = os.path.join(reports_base, parent_dir_id, "run-id", hashed_name)
            ok, final_name = rename_from_temp_hash(hashed_path, hashed_name, new_idx, sub_idx, temp_hash)
            if ok:
                log.info("PASS 2 (final): %s → %s", hashed_name, final_name)
                final_path = os.path.join(reports_base, parent_dir_id, "run-id", final_name)

                # Move duplicate folders (sub_idx > 0) into [parent_dir_id]/_duplicate/
                # sitting side-by-side with run-id. The cfg@N-1, cfg@N-2 names are kept.
                if sub_idx > 0:
                    dup_dir = os.path.join(reports_base, parent_dir_id, "_duplicate")
                    os.makedirs(dup_dir, exist_ok=True)
                    dup_dst = os.path.join(dup_dir, final_name)
                    if os.path.exists(dup_dst):
                        log.warning("DUPLICATE MOVE SKIPPED (already exists): %s", dup_dst)
                    else:
                        try:
                            shutil.move(final_path, dup_dst)
                            log.info("DUPLICATE MOVED: %s → %s", final_name, dup_dst)
                            duplicate_count += 1
                        except Exception as e:
                            log.error("DUPLICATE MOVE FAILED: %s: %s", final_name, e)

                # For non-duplicates, optionally archive old name as backup
                # (skip if --force or --no-archive)
                elif not no_archive and not force:
                    ok2, msg2 = move_to_archive(final_path, REPORTS_SHIFTED, parent_dir_id, final_name)
                    if ok2:
                        log.info("ARCHIVED BACKUP: %s (to %s)", final_name, msg2)
                    else:
                        log.warning("ARCHIVE BACKUP FAILED: %s (but rename succeeded, continuing)", msg2)

                renamed_count += 1
            else:
                log.error("PASS 2 FAILED (final): %s", final_name)
                skipped_count += 1

    log.info("%s", "=" * LINE_LENGTH)
    log.info(
        "Summary for %s: %d renamed, %d skipped, %d orphaned, %d duplicates copied",
        parent_dir_id, renamed_count, skipped_count, orphaned_count, duplicate_count
    )
    if duplicates:
        log.info(
            "Duplicate cfg@ indices: %d index(es) had multiple folders — %s",
            len(duplicates),
            ", ".join(f"cfg@{idx:02d}({len(items)})" for idx, items in sorted(duplicates.items()))
        )
    if duplicate_count > 0:
        log.info("(Duplicate folders also copied to: %s)", REPORTS_DUPLICATE)
    if orphaned_count > 0:
        log.info("(Orphaned folders archived to: %s)", REPORTS_ORPHANED)
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
    return [pid for pid in pids if pid]


# ------------------------------------------------------------------------------------------------------------------- #
# MAIN
# ------------------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Batch Shifter: Rename cfg@N folders when batch configs are reordered/commented"
    )

    parser.add_argument(
        "-pid", "--parent-dir-id", type=str, required=False,
        help="Process specific parent_dir_id(s) separated by comma (e.g., 'ql-p-ms@0' or 'ql-p-ms@0,ql-p-ms@1'). Located under report base directory."
    )

    parser.add_argument(
        "-a", "--all", action="store_true",
        help="Process all parent_dir_ids in report base directory"
    )

    parser.add_argument(
        "-srp", "--setreportspath", type=str, required=False,
        help="Override base report directory path. Accepts absolute paths (e.g., 'D:/test/newdir') or relative paths from current working directory (e.g., 'custom/reports'). Default: 'reports/skripsi'"
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

    parser.add_argument(
        "-f", "--force", action="store_true",
        help="Use two-pass rename with temporary hashing to prevent collisions (skips archiving)"
    )

    args = parser.parse_args()

    if not args.all and not args.parent_dir_id:
        log.error("Specify either --parent-dir-id or --all")
        sys.exit(1)

    if args.all and args.parent_dir_id:
        log.error("Cannot specify both --all and --parent-dir-id")
        sys.exit(1)

    normalized_report_base = normalize_report_base(args.setreportspath or REPORTS_BASE)

    if not os.path.isdir(normalized_report_base):
        log.error("Reports directory not found: %s", normalized_report_base)
        sys.exit(1)

    total_renamed = 0
    total_skipped = 0

    if args.all:
        parent_dir_ids = [
            item for item in os.listdir(normalized_report_base)
            if os.path.isdir(os.path.join(normalized_report_base, item))
        ]

        if not parent_dir_ids:
            log.warning("No parent_dir_ids found in %s", normalized_report_base)
            sys.exit(0)

        log.info("Found %d parent_dir_ids: %s", len(parent_dir_ids), parent_dir_ids)

        for pid in sorted(parent_dir_ids):
            renamed, skipped = execute_shift(
                pid,
                reports_base=normalized_report_base,
                index_only=args.indexonly,
                dry_run=args.dry_run,
                no_archive=args.no_archive,
                force=args.force
            )
            total_renamed += renamed
            total_skipped += skipped
    else:
        parent_dir_ids = parse_parent_dir_ids(args.parent_dir_id)

        if not parent_dir_ids:
            log.error("No valid parent_dir_ids provided")
            sys.exit(1)

        log.info("Processing %d parent_dir_id(s): %s", len(parent_dir_ids), parent_dir_ids)

        for pid in parent_dir_ids:
            renamed, skipped = execute_shift(
                pid,
                reports_base=normalized_report_base,
                index_only=args.indexonly,
                dry_run=args.dry_run,
                no_archive=args.no_archive,
                force=args.force
            )
            total_renamed += renamed
            total_skipped += skipped

    log.info("%s", "=" * LINE_LENGTH)
    if args.dry_run:
        log.info("[DRY RUN] Total: %d would be renamed, %d skipped", total_renamed, total_skipped)
    else:
        log.info("[EXECUTION] Total: %d renamed, %d skipped", total_renamed, total_skipped)
    log.info("%s", "=" * LINE_LENGTH)

    sys.exit(0 if total_skipped == 0 else 1)