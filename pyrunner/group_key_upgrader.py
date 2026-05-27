"""
Group Key Upgrader: Add cg@{group} token to existing run-id directories.

Supports:
- default hardcoded batch_configs.py
- optional custom config module via --config-module
- dry-run mode
- batch processing
- replace existing group tokens via --replacegroup

Examples:

# Use default batch_configs.py
python pyrunner/group_key_upgrader.py --parent-dir-id ql-p-ms@0 --dry-run

# Short version
python pyrunner/group_key_upgrader.py -pid ql-p-ms@0 --dry-run

# Use custom batch_configs_jord.py
python pyrunner/group_key_upgrader.py \
    -pid ql-p-ms@0 \
    --config-module pyrunner.batch_configs_jord \
    --dry-run

# Replace existing group tokens
python pyrunner/group_key_upgrader.py \
    -pid ql-p-ms@0 \
    --replacegroup \
    --dry-run

# Short version with replace
python pyrunner/group_key_upgrader.py -pid ql-p-ms@0 -rg --dry-run

# Process all directories
python pyrunner/group_key_upgrader.py --all

# Short version
python pyrunner/group_key_upgrader.py -a

# Process all using custom configs and replace groups
python pyrunner/group_key_upgrader.py \
    -a \
    --config-module pyrunner.batch_configs_jord \
    --replacegroup
"""

import argparse
import importlib
import json
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

# Default config import (fallback)
from pyrunner.batch_configs_jord import LIST_OF_CONFIGS

from pyrunner.utils.path import normalize_report_base

LINE_LENGTH = 100

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)

log = logging.getLogger(__name__)

REPORTS_BASE = r"reports/skripsi"


# ============================================================================
# Config Loader
# ============================================================================

def load_list_of_configs(config_module_path: Optional[str]):
    """
    Load LIST_OF_CONFIGS from a custom module if provided.
    Otherwise use the default imported LIST_OF_CONFIGS.
    """

    if not config_module_path:
        log.info("Using default LIST_OF_CONFIGS from pyrunner.batch_configs")
        return LIST_OF_CONFIGS

    try:
        module = importlib.import_module(config_module_path)

    except Exception as e:
        log.error(
            "Failed to import config module '%s': %s",
            config_module_path,
            e
        )
        sys.exit(1)

    if not hasattr(module, "LIST_OF_CONFIGS"):
        log.error(
            "Module '%s' does not contain LIST_OF_CONFIGS",
            config_module_path
        )
        sys.exit(1)

    log.info("Using LIST_OF_CONFIGS from %s", config_module_path)

    return module.LIST_OF_CONFIGS


# ============================================================================
# Folder Parsing
# ============================================================================

def extract_cfg_index(folder_name: str) -> Optional[int]:
    """
    Extract cfg index from folder name like:
        cfg@05-ql500-...
    """

    match = re.match(r"cfg@(\d+)", folder_name)

    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass

    return None


def extract_alg_and_runs(folder_name: str) -> Optional[Tuple[str, int]]:
    """
    Extract algorithm and runs from folder name.

    Supports:
        cfg@05-ql500-...
        cfg@05-cg@...-ql500-...
    """

    match = re.search(
        r"(?:cfg@\d+-(?:cg@[^\-]+-)?)(\w+?)(\d+)",
        folder_name
    )

    if match:
        alg = match.group(1)

        try:
            runs = int(match.group(2))
            return alg, runs

        except ValueError:
            pass

    return None


def extract_behavior_policy(folder_name: str) -> Optional[str]:
    r"""
    Extract behavior policy from folder name.
    Accounts for optional group token: cfg@\d+(-cg@{group})?-ql\d+
    """

    # Q-learning
    # Matches: cfg@\d+-ql\d+ OR cfg@\d+-cg@...-ql\d+
    if re.search(r"cfg@\d+(?:-cg@[^\-]+)?-ql\d+", folder_name):

        match = re.search(r"qlm_bp@(\w+)", folder_name)

        if match:
            return match.group(1)

        return "epsilon"

    # Monte Carlo
    # Matches: cfg@\d+-mcn\d+ OR cfg@\d+-cg@...-mcn\d+
    if re.search(r"cfg@\d+(?:-cg@[^\-]+)?-mcn\d+", folder_name):

        match = re.search(r"bp@(\w+)", folder_name)

        if match:
            return match.group(1)

        return "epsilon"

    # Lévy Flight
    # Matches: cfg@\d+-lfe\d+ OR cfg@\d+-cg@...-lfe\d+
    if re.search(r"cfg@\d+(?:-cg@[^\-]+)?-lfe\d+", folder_name):
        return None

    return None


def has_group_token(folder_name: str) -> bool:
    """
    Check if folder already contains cg@
    """

    return "cg@" in folder_name


def extract_existing_group(folder_name: str) -> Optional[str]:
    """
    Extract the existing group from folder name.
    
    Example: cfg@05-cg@ql_ps-ql500-... -> "ql_ps"
    """

    match = re.search(r"cg@([^\-]+)", folder_name)

    if match:
        return match.group(1)

    return None


def replace_group_token(
        folder_name: str,
        new_group: str
) -> str:
    """
    Replace existing cg@{old_group} with cg@{new_group}.
    
    Example: cfg@05-cg@ql_ps-ql500-... -> cfg@05-cg@ql_ps_bbts-ql500-...
    """

    return re.sub(
        r"(cfg@\d+)-cg@[^\-]+",
        f"\\1-cg@{new_group}",
        folder_name
    )


# ============================================================================
# Config Setting JSON Updates
# ============================================================================

def update_config_setting_json(
        folder_path: str,
        old_folder_name: str,
        new_folder_name: str
) -> Tuple[int, int]:
    """
    Update config_setting.json files in the folder.
    
    Returns: (updated_count, failed_count)
    """

    updated = 0
    failed = 0

    # Find all config_setting.json files
    for root, dirs, files in os.walk(folder_path):
        if "config_setting.json" in files:
            config_path = os.path.join(root, "config_setting.json")

            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)

            except Exception as e:
                log.warning(
                    "Failed to read config_setting.json '%s': %s",
                    config_path,
                    e
                )
                failed += 1
                continue

            modified = False

            # Update runner_id field
            if "runner_id" in config_data:
                if config_data["runner_id"] == old_folder_name:
                    config_data["runner_id"] = new_folder_name
                    modified = True

            # Update highlighted_settings persistence path
            if "highlighted_settings" in config_data:
                if "EpisodicPersistenceManager.persistencePath" in config_data["highlighted_settings"]:
                    old_path = config_data["highlighted_settings"]["EpisodicPersistenceManager.persistencePath"]
                    new_path = old_path.replace(old_folder_name, new_folder_name)

                    if old_path != new_path:
                        config_data["highlighted_settings"]["EpisodicPersistenceManager.persistencePath"] = new_path
                        modified = True

            # Update overridden_settings persistence path
            if "overridden_settings" in config_data:
                if "EpisodicPersistenceManager.persistencePath" in config_data["overridden_settings"]:
                    old_path = config_data["overridden_settings"]["EpisodicPersistenceManager.persistencePath"]
                    new_path = old_path.replace(old_folder_name, new_folder_name)

                    if old_path != new_path:
                        config_data["overridden_settings"]["EpisodicPersistenceManager.persistencePath"] = new_path
                        modified = True

            # Write back if modified
            if modified:
                try:
                    with open(config_path, 'w', encoding='utf-8') as f:
                        json.dump(config_data, f, indent=4)

                    log.info(
                        "Updated config_setting.json: %s",
                        config_path
                    )
                    updated += 1

                except Exception as e:
                    log.error(
                        "Failed to write config_setting.json '%s': %s",
                        config_path,
                        e
                    )
                    failed += 1

    return updated, failed


# ============================================================================
# Config Matching
# ============================================================================

def build_config_signature(
        alg: str,
        runs: int,
        bp: Optional[str] = None
) -> str:

    sig = f"{alg}+{runs}"

    if bp:
        sig = f"{sig}+{bp}"

    return sig


def get_active_configs_mapping(list_of_configs) -> Dict[int, dict]:
    """
    Build cfg index -> config mapping.
    """

    mapping = {}

    for idx, config in enumerate(list_of_configs, start=1):
        mapping[idx] = config

    return mapping


# ============================================================================
# Folder Scanner
# ============================================================================

def scan_run_id_folders(
        parent_dir_id: str,
        reports_base: str = REPORTS_BASE
) -> Dict[int, str]:

    run_id_path = os.path.join(
        reports_base,
        parent_dir_id,
        "run-id"
    )

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


# ============================================================================
# Upgrade Mapping
# ============================================================================

def build_upgrade_mapping(
        existing_folders: Dict[int, str],
        active_configs: Dict[int, dict],
        replace_mode: bool = False
) -> Tuple[Dict[str, str], List[str]]:

    rename_mapping = {}
    messages = []

    # Map signature to list of possible groups (handles multiple groups per sig)
    sig_to_groups: Dict[str, List[str]] = {}
    # Also keep mapping of config index to group for specific assignments
    idx_to_group: Dict[int, str] = {}

    for idx, config in active_configs.items():

        alg = config["alg"]
        runs = config["runs"]
        bp = config.get("bp")
        group = config.get("group")

        sig = build_config_signature(alg, runs, bp)

        # Store mapping for specific config index
        if group:
            idx_to_group[idx] = group

        # Store all possible groups for this signature
        if sig not in sig_to_groups:
            sig_to_groups[sig] = []

        if group and group not in sig_to_groups[sig]:
            sig_to_groups[sig].append(group)

    # Process folders
    for cfg_idx, old_folder_name in sorted(existing_folders.items()):

        alg_runs = extract_alg_and_runs(old_folder_name)

        if not alg_runs:
            messages.append(
                f"cfg@{cfg_idx:02d}: Failed to extract alg+runs"
            )
            continue

        alg, runs = alg_runs

        bp = extract_behavior_policy(old_folder_name)

        sig = build_config_signature(alg, runs, bp)

        if sig not in sig_to_groups:
            messages.append(
                f"cfg@{cfg_idx:02d}: No matching config for sig={sig}"
            )
            continue

        possible_groups = sig_to_groups[sig]

        if not possible_groups:
            messages.append(
                f"cfg@{cfg_idx:02d}: Matching config has no group"
            )
            continue

        # Get the correct group for this specific config index
        correct_group = idx_to_group.get(cfg_idx)

        # Handle folders that already have a group token
        if has_group_token(old_folder_name):

            existing_group = extract_existing_group(old_folder_name)

            # Check if existing group is valid for this signature
            if existing_group in possible_groups:
                # If it's the correct one for this config, skip it
                if correct_group and existing_group == correct_group:
                    messages.append(
                        f"cfg@{cfg_idx:02d}: [SKIP] Already has correct group "
                        f"(cg@{existing_group})"
                    )
                    continue

                # If it's valid but different from what config specifies, optionally replace
                if replace_mode and correct_group and existing_group != correct_group:
                    new_group = correct_group

                    new_folder_name = replace_group_token(old_folder_name, new_group)

                    rename_mapping[old_folder_name] = new_folder_name

                    messages.append(
                        f"cfg@{cfg_idx:02d}: [REPLACE] "
                        f"'{old_folder_name}' -> '{new_folder_name}' "
                        f"(cg@{existing_group} -> cg@{new_group})"
                    )

                    continue

                # Valid group but no replace mode or no correct_group
                messages.append(
                    f"cfg@{cfg_idx:02d}: [SKIP] Already has valid group "
                    f"(cg@{existing_group})"
                )
                continue

            # Existing group is not in the valid list
            if not replace_mode:
                messages.append(
                    f"cfg@{cfg_idx:02d}: Has invalid group (cg@{existing_group}), "
                    f"skipping (use --replacegroup to update)"
                )
                continue

            # Replace with the correct group for this config index
            new_group = correct_group if correct_group else possible_groups[0]

            new_folder_name = replace_group_token(old_folder_name, new_group)

            rename_mapping[old_folder_name] = new_folder_name

            messages.append(
                f"cfg@{cfg_idx:02d}: [REPLACE] "
                f"'{old_folder_name}' -> '{new_folder_name}' "
                f"(cg@{existing_group} -> cg@{new_group})"
            )

            continue

        # Insert cg@ for folders without group token
        # Use the correct group for this specific config index
        new_group = correct_group if correct_group else possible_groups[0]

        new_folder_name = re.sub(
            r"^(cfg@\d+)-",
            f"\\1-cg@{new_group}-",
            old_folder_name
        )

        rename_mapping[old_folder_name] = new_folder_name

        messages.append(
            f"cfg@{cfg_idx:02d}: [ADD] "
            f"'{old_folder_name}' -> '{new_folder_name}'"
        )

    return rename_mapping, messages


# ============================================================================
# Rename Executor
# ============================================================================

def execute_renames(
        parent_dir_id: str,
        rename_mapping: Dict[str, str],
        reports_base: str = REPORTS_BASE,
        dry_run: bool = True
) -> Tuple[int, int, int]:

    run_id_path = os.path.join(
        reports_base,
        parent_dir_id,
        "run-id"
    )

    total = len(rename_mapping)
    successes = 0
    failures = 0

    for old_name, new_name in rename_mapping.items():

        old_path = os.path.join(run_id_path, old_name)
        new_path = os.path.join(run_id_path, new_name)

        if not os.path.exists(old_path):
            log.warning("Source not found: %s", old_path)
            failures += 1
            continue

        if os.path.exists(new_path):
            log.warning("Destination exists: %s", new_path)
            failures += 1
            continue

        if dry_run:
            log.info("[DRY-RUN] %s -> %s", old_name, new_name)
            successes += 1

        else:
            try:
                shutil.move(old_path, new_path)

                log.info("Renamed: %s -> %s", old_name, new_name)

                # Update config_setting.json files in the renamed folder
                updated_configs, failed_configs = update_config_setting_json(
                    new_path,
                    old_name,
                    new_name
                )

                if failed_configs > 0:
                    log.warning(
                        "Failed to update %d config_setting.json files in %s",
                        failed_configs,
                        new_name
                    )
                    failures += 1
                else:
                    successes += 1

            except Exception as e:
                log.error(
                    "Failed rename '%s': %s",
                    old_name,
                    e
                )

                failures += 1

    return total, successes, failures


# ============================================================================
# Parent Dir Processor
# ============================================================================

def process_parent_dir(
        parent_dir_id: str,
        list_of_configs,
        reports_base: str = REPORTS_BASE,
        dry_run: bool = True,
        replace_mode: bool = False
) -> Tuple[int, int, int]:

    log.info("%s", "=" * LINE_LENGTH)
    log.info("Processing: %s", parent_dir_id)
    log.info("%s", "=" * LINE_LENGTH)

    existing_folders = scan_run_id_folders(
        parent_dir_id,
        reports_base
    )

    if not existing_folders:
        log.warning("No run-id folders found")
        return 0, 0, 0

    log.info(
        "Found %d run-id folders",
        len(existing_folders)
    )

    active_configs = get_active_configs_mapping(list_of_configs)

    rename_mapping, info_messages = build_upgrade_mapping(
        existing_folders,
        active_configs,
        replace_mode
    )

    for msg in info_messages:
        log.info("  %s", msg)

    if not rename_mapping:
        log.info("Nothing to upgrade")
        return 0, 0, 0

    total, successes, failures = execute_renames(
        parent_dir_id,
        rename_mapping,
        reports_base,
        dry_run
    )

    log.info(
        "Result: total=%d success=%d failed=%d",
        total,
        successes,
        failures
    )

    return total, successes, failures


# ============================================================================
# Main
# ============================================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Upgrade run-id directories to include cg@ group token"
        )
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Process all parent directories"
    )

    group.add_argument(
        "--parent-dir-id",
        "-pid",
        type=str,
        help="Comma-separated parent dir IDs"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without renaming"
    )

    parser.add_argument(
        "--replacegroup",
        "-rg",
        action="store_true",
        help="Replace existing group tokens according to batch_configs"
    )

    parser.add_argument(
        "--reports-base",
        type=str,
        default=REPORTS_BASE,
        help=f"Base reports directory (default: {REPORTS_BASE})"
    )

    parser.add_argument(
        "--config-module",
        type=str,
        default=None,
        help=(
            "Optional custom config module "
            "(example: pyrunner.batch_configs_jord)"
        )
    )

    args = parser.parse_args()

    # Load configs
    list_of_configs = load_list_of_configs(args.config_module)

    log.info(
        "Loaded %d configs",
        len(list_of_configs)
    )

    normalized_report_base = normalize_report_base(
        args.reports_base
    )

    start_time = datetime.now()

    total_renames = 0
    total_successes = 0
    total_failures = 0

    # ========================================================================
    # Process all
    # ========================================================================

    if args.all:

        report_path = os.path.join(normalized_report_base)

        if not os.path.isdir(report_path):
            log.error(
                "Reports base directory not found: %s",
                report_path
            )
            sys.exit(1)

        parent_dirs = sorted([
            d for d in os.listdir(report_path)
            if os.path.isdir(os.path.join(report_path, d))
            and os.path.isdir(os.path.join(report_path, d, "run-id"))
        ])

        if not parent_dirs:
            log.warning("No run-id directories found")
            sys.exit(0)

        log.info(
            "Found %d parent directories",
            len(parent_dirs)
        )

        for parent_dir in parent_dirs:

            total, successes, failures = process_parent_dir(
                parent_dir,
                list_of_configs,
                normalized_report_base,
                args.dry_run,
                args.replacegroup
            )

            total_renames += total
            total_successes += successes
            total_failures += failures

    # ========================================================================
    # Process selected dirs
    # ========================================================================

    else:

        parent_dirs = [
            d.strip()
            for d in args.parent_dir_id.split(",")
        ]

        for parent_dir in parent_dirs:

            total, successes, failures = process_parent_dir(
                parent_dir,
                list_of_configs,
                normalized_report_base,
                args.dry_run,
                args.replacegroup
            )

            total_renames += total
            total_successes += successes
            total_failures += failures

    # ========================================================================
    # Summary
    # ========================================================================

    elapsed = datetime.now() - start_time

    log.info("%s", "=" * LINE_LENGTH)

    log.info(
        "[SUMMARY] Completed in %s",
        elapsed
    )

    log.info(
        "Total=%d Success=%d Failed=%d",
        total_renames,
        total_successes,
        total_failures
    )

    if args.dry_run:
        log.info(
            "This was a DRY-RUN. Remove --dry-run to apply changes."
        )

    log.info("%s", "=" * LINE_LENGTH)


if __name__ == "__main__":
    main()