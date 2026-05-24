"""
model_extractor.py — Single Episode Model Extraction

Extracts a single episode from an existing run directory into a fresh parent
directory structure, normalizing the extracted episode as episode 0 (base/previous weight).

This module creates a new run directory hierarchy suitable for deployment or analysis:
  - Defaults to extracting the last (highest) episode from the source run
  - Normalizes all episodeNumber fields to 0 in the extracted episode
  - Derives _persistence.json from the extracted episode's Persistence-Episode@0.json
  - Preserves config_setting.json as-is (for reference of original run parameters)

Two modes for specifying the source:
  - Signature mode (-fs):  matches run dirs containing alg+runs in their name
  - Config mode    (-c):   matches run dirs by cfg@N pattern (comma/range)

Output naming:
  - By default: prepends 'sampled-<original_pid>' to create a new parent directory
  - With --aspid: uses specified directory as parent instead

Usage examples:
  # Extract last episode by config index
  python model_extractor.py -pid skripsi-run1 -c 3

  # Extract specific episode by signature
  python model_extractor.py -pid skripsi-run1 -fs lfe500 --ofepisode 500

  # Extract to custom parent directory with custom reports path
  python model_extractor.py -pid skripsi-run1 -c 3 --aspid custom-parent -srp D:/reports
"""

# ------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------------------------------------------- #

import argparse
import json
import logging
import os
import re
import shutil
import sys
from typing import Optional, Tuple

# Allow running as a script while still using absolute package imports (pyrunner.*)
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.utils.fs import safe_int_dirnames
from pyrunner.utils.jsonio import load_json_file
from pyrunner.utils.path import normalize_report_base
from pyrunner.batch_shifter import extract_alg_and_runs

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

SAMPLED_INITIAL_EPISODE = 0

# Default base directory for all report outputs (mirrors episode_extender.py)
REPORTS_BASE = "reports/skripsi"


# ------------------------------------------------------------------------------------------------------------------- #
# DIRECTORY RESOLUTION
# ------------------------------------------------------------------------------------------------------------------- #

def _parse_config_indices(config_string: str) -> list[int]:
    """
    Parse config indices from a string supporting single values and ranges.

    Examples:
        "3"        → [3]
        "1,2,5"    → [1, 2, 5]
        "4-6"      → [4, 5, 6]
        "1,3-5,9"  → [1, 3, 4, 5, 9]
    """
    configs: set[int] = set()

    for part in config_string.split(","):
        part = part.strip()
        if not part:
            continue

        if "-" in part:
            try:
                start_str, end_str = part.split("-", 1)
                start, end = int(start_str.strip()), int(end_str.strip())
                if start > end:
                    raise ValueError(f"Invalid range '{part}': start > end")
                configs.update(range(start, end + 1))
            except ValueError as exc:
                raise ValueError(f"Invalid range format '{part}': {exc}") from exc
        else:
            try:
                configs.add(int(part))
            except ValueError as exc:
                raise ValueError(f"Invalid config number '{part}'") from exc

    return sorted(configs)


def _cfg_index_from_folder(folder_name: str) -> Optional[int]:
    """
    Extract the cfg@N index from a run-dir folder name.

    Folder names follow the pattern: cfg@NN[-cg@G]-alg+runs[-overrides...]
    Examples:
        cfg@03-lfe500-...   → 3
        cfg@12-cg@A-ql500   → 12
    """
    m = re.match(r"^cfg@(\d+)", folder_name)
    return int(m.group(1)) if m else None


def find_matching_run_dirs(
        parent_dir_id: str,
        reports_base: str,
        *,
        config_indices: Optional[list[int]] = None,
        from_signature: Optional[str] = None,
) -> list[str]:
    """
    Scan the run-id directory and return full paths of folders that satisfy
    ALL provided filters.  At least one filter must be given.

    Filters (all applied with AND logic):
        config_indices   – folder's cfg@N must be in the list
        from_signature   – folder must contain alg+runs matching the signature
                           (e.g. 'lfe500' → alg='lfe', runs=500)

    Returns a list of matching full directory paths (may be empty).
    """
    if not config_indices and not from_signature:
        raise ValueError("At least one of config_indices or from_signature must be provided")

    run_id_path = os.path.join(reports_base, parent_dir_id, "run-id")
    if not os.path.isdir(run_id_path):
        log.warning("run-id directory not found: %s", run_id_path)
        return []

    # Pre-parse signature once
    expected_alg: Optional[str] = None
    expected_runs: Optional[int] = None
    if from_signature:
        sig_match = re.match(r"^(\w+?)(\d+)$", from_signature)
        if not sig_match:
            raise ValueError(
                f"Invalid signature format '{from_signature}'. Expected format like 'lfe500'."
            )
        expected_alg = sig_match.group(1)
        expected_runs = int(sig_match.group(2))

    matches: list[str] = []

    for folder_name in sorted(os.listdir(run_id_path)):
        folder_path = os.path.join(run_id_path, folder_name)
        if not os.path.isdir(folder_path):
            continue

        # ── Filter 1: cfg@N index ──────────────────────────────────────────
        if config_indices is not None:
            idx = _cfg_index_from_folder(folder_name)
            if idx is None or idx not in config_indices:
                continue

        # ── Filter 2: alg+runs signature ──────────────────────────────────
        if expected_alg is not None:
            alg_runs = extract_alg_and_runs(folder_name)
            if alg_runs is None:
                continue
            alg, runs = alg_runs
            if alg != expected_alg or runs != expected_runs:
                continue

        matches.append(folder_path)

    return matches


# ------------------------------------------------------------------------------------------------------------------- #
# VALIDATION & PERSISTENCE HELPERS
# ------------------------------------------------------------------------------------------------------------------- #

def validate_source_config(full_report_dir: str) -> Tuple[bool, str, dict]:
    """
    Load and validate the source run's config_setting.json.

    Returns: (is_valid, message, config_dict)
    """
    config_file = os.path.join(full_report_dir, "config_setting.json")

    if not os.path.isfile(config_file):
        return False, f"config_setting.json not found: {config_file}", {}

    ok, config, err = load_json_file(config_file)
    if not ok:
        return False, f"Failed to load config_setting.json: {err}", {}

    # Backwards-compatibility: migrate deprecated key "runner_nrof_episodes:" → "runner_nrof_episodes"
    bad_key  = "runner_nrof_episodes:"
    good_key = "runner_nrof_episodes"
    if bad_key in config:
        config[good_key] = config.pop(bad_key)
        log.warning("Migrated deprecated key '%s' → '%s' (in-memory only)", bad_key, good_key)

    required = ["runner_algorithm", "runner_nrof_episodes", "runner_id"]
    missing = [f for f in required if f not in config]
    if missing:
        return False, f"config_setting.json missing required fields: {missing}", config

    return True, "Validated successfully", config


def find_highest_episode(ep_root: str) -> Tuple[int, list[str]]:
    """
    Find the highest episode number available in the ep directory.

    Returns: (highest_episode, problems)
             highest_episode == 0 when no episodes exist.
    """
    problems: list[str] = []

    if not os.path.isdir(ep_root):
        problems.append(f"Episodic directory missing: {ep_root}")
        return 0, problems

    episode_dirs = safe_int_dirnames(ep_root)
    if not episode_dirs:
        problems.append(f"No episode directories found under: {ep_root}")
        return 0, problems

    highest = max(episode_dirs)
    
    # Validate that the highest episode has readable persistence
    persistence_path = os.path.join(
        ep_root, str(highest), f"Persistence-Episode@{highest}.json"
    )
    ok, data, err = load_json_file(persistence_path)
    if not ok:
        problems.append(f"Highest episode {highest} unreadable: {persistence_path} ({err})")
        return 0, problems

    return highest, problems


# ------------------------------------------------------------------------------------------------------------------- #
# EPISODE NORMALIZATION
# ------------------------------------------------------------------------------------------------------------------- #

def normalize_episode_to_one(
        source_ep_dir: str,
        target_ep_dir: str,
        source_episode_num: int,
) -> Tuple[bool, str]:
    """
    Copy only Persistence-Episode@{source_episode_num}.json to target ep/SAMPLED_INITIAL_EPISODE,
    renaming it to Persistence-Episode@SAMPLED_INITIAL_EPISODE.json and normalizing episodeNumber.
    
    Skips all other files (CSV reports, etc.) to keep the extracted episode minimal.

    Returns: (success, message)
    """
    source_ep_path = os.path.join(source_ep_dir, str(source_episode_num))
    target_ep_path = os.path.join(target_ep_dir, str(SAMPLED_INITIAL_EPISODE))

    if not os.path.isdir(source_ep_path):
        return False, f"Source episode directory not found: {source_ep_path}"

    try:
        # Create target episode directory
        if os.path.exists(target_ep_path):
            shutil.rmtree(target_ep_path)
        os.makedirs(target_ep_path, exist_ok=True)

        # Find and copy only the Persistence-Episode@{source_episode_num}.json file
        source_persistence_file = f"Persistence-Episode@{source_episode_num}.json"
        source_persistence_path = os.path.join(source_ep_path, source_persistence_file)
        
        if not os.path.isfile(source_persistence_path):
            return False, f"Persistence file not found: {source_persistence_path}"

        # Copy with renamed filename to target
        target_persistence_file = f"Persistence-Episode@{SAMPLED_INITIAL_EPISODE}.json"
        target_persistence_path = os.path.join(target_ep_path, target_persistence_file)

        ok, data, err = load_json_file(source_persistence_path)
        if not ok:
            return False, f"Failed to read persistence file: {err}"

        # Update episodeNumber to target episode
        if "episodeNumber" in data:
            old_value = data["episodeNumber"]
            data["episodeNumber"] = SAMPLED_INITIAL_EPISODE
            log.debug("Updated episodeNumber in persistence: %s → %d", old_value, SAMPLED_INITIAL_EPISODE)

        # Write to target location with new name
        with open(target_persistence_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, sort_keys=True)

        return True, f"Copied and normalized {source_persistence_file} → {target_persistence_file} (episode {source_episode_num} → {SAMPLED_INITIAL_EPISODE})"

    except Exception as exc:
        return False, f"Failed during episode normalization: {exc}"


def create_persistence_from_episode(
        source_ep_dir: str,
        target_root_dir: str,
) -> Tuple[bool, str]:
    """
    Create _persistence.json in target root from the normalized Persistence-Episode@SAMPLED_INITIAL_EPISODE.json.

    Returns: (success, message)
    """
    try:
        source_persistence = os.path.join(source_ep_dir, str(SAMPLED_INITIAL_EPISODE), f"Persistence-Episode@{SAMPLED_INITIAL_EPISODE}.json")
        target_persistence = os.path.join(target_root_dir, "_persistence.json")

        ok, data, err = load_json_file(source_persistence)
        if not ok:
            return False, f"Cannot read source persistence: {source_persistence} ({err})"

        # Ensure episodeNumber is SAMPLED_INITIAL_EPISODE in the root persistence as well
        if "episodeNumber" in data:
            data["episodeNumber"] = SAMPLED_INITIAL_EPISODE

        with open(target_persistence, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, sort_keys=True)

        return True, f"Created _persistence.json from Persistence-Episode@{SAMPLED_INITIAL_EPISODE}.json"

    except Exception as exc:
        return False, f"Failed to create _persistence.json: {exc}"


def replace_alg_runs_in_runner_id(runner_id: str, alg: str, old_runs: int, new_runs: int) -> str:
    """
    Replace the alg+runs token inside a runner_id string.

    Example:    cfg@03-lfe500-bp@ps  →  cfg@03-lfe10-bp@ps
    Or:         cfg@03-cg@lf-lfe500-bp@ps  →  cfg@03-cg@lf-lfe10-bp@ps
    """
    pattern     = rf"\b{re.escape(alg)}{old_runs}\b"
    replacement = f"{alg}{new_runs}"
    updated     = re.sub(pattern, replacement, runner_id, count=1)

    if updated == runner_id:
        raise ValueError(
            f"Could not find '{alg}{old_runs}' to replace in runner_id: '{runner_id}'"
        )
    return updated


def update_config_setting_for_extraction(
        full_report_dir: str,
        new_runner_id: str,
        new_episodes: int,
) -> Tuple[bool, str]:
    """
    Update config_setting.json with the new runner_id and episode count.
    Also updates alg+runs patterns in highlighted_settings and overridden_settings.

    Keys updated:
        runner_id             ← new_runner_id
        runner_nrof_episodes  ← new_episodes
        highlighted_settings[EpisodicPersistenceManager.persistencePath] ← regex with new runs
        overridden_settings[...persistencePath...] ← regex with new runs

    Returns: (success, message)
    """
    config_file = os.path.join(full_report_dir, "config_setting.json")
    tmp_file    = config_file + ".tmp"

    ok, config, err = load_json_file(config_file)
    if not ok:
        return False, f"Cannot read config_setting.json: {err}"

    try:
        # Migrate deprecated key just in case
        bad_key  = "runner_nrof_episodes:"
        good_key = "runner_nrof_episodes"
        if bad_key in config:
            del config[bad_key]

        old_runner_id = config.get("runner_id", "unknown")
        old_episodes  = config.get(good_key, "unknown")

        config[good_key]    = new_episodes
        config["runner_id"] = new_runner_id

        # Update highlighted_settings if present (regex patterns with persistencePath)
        highlighted_settings = config.get("highlighted_settings", {})
        if highlighted_settings:
            for key in list(highlighted_settings.keys()):
                value = highlighted_settings[key]
                # Replace old_runner_id with new_runner_id in any string values
                if isinstance(value, str) and old_runner_id in value:
                    highlighted_settings[key] = value.replace(str(old_runner_id), str(new_runner_id))
        config["highlighted_settings"] = highlighted_settings

        # Update overridden_settings if present (list of override dicts with persistencePath)
        overridden_settings = config.get("overridden_settings", [])
        if overridden_settings and isinstance(overridden_settings, list):
            for override_dict in overridden_settings:
                if isinstance(override_dict, dict):
                    for key in list(override_dict.keys()):
                        value = override_dict[key]
                        # Replace old_runner_id with new_runner_id in any string values
                        if isinstance(value, str) and old_runner_id in value:
                            override_dict[key] = value.replace(str(old_runner_id), str(new_runner_id))
        config["overridden_settings"] = overridden_settings

        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4, sort_keys=True)

        os.replace(tmp_file, config_file)

        return True, (
            f"config_setting.json updated:\n"
            f"  runner_id:            {old_runner_id!r} → {new_runner_id!r}\n"
            f"  runner_nrof_episodes: {old_episodes} → {new_episodes}"
        )
    except Exception as exc:
        try:
            if os.path.exists(tmp_file):
                os.remove(tmp_file)
        except OSError:
            pass
        return False, f"Failed to write config_setting.json: {exc}"


# ------------------------------------------------------------------------------------------------------------------- #
# MAIN EXTRACTION LOGIC
# ------------------------------------------------------------------------------------------------------------------- #

def extract_model(
        source_dir: str,
        source_episode: int,
        target_parent_dir_id: str,
        reports_base: str,
        episodesig: int = 10,
) -> None:
    """
    Core extraction routine for a single matched source directory.

    Steps:
        1. Validate config_setting.json
        2. Verify selected episode exists and is readable
        3. Create target directory structure
        4. Copy and normalize episode to ep/SAMPLED_INITIAL_EPISODE
        5. Create _persistence.json from normalized episode
        6. Copy config_setting.json to target root, updating runner_id and episode count
        7. Log summary
    """
    log.info("%s", "=" * LINE_LENGTH)
    log.info("[EXTRACT] Source: %s", source_dir)

    # ── Step 1: Validate source config ────────────────────────────────────
    is_valid, msg, source_config = validate_source_config(source_dir)
    if not is_valid:
        log.error("[EXTRACT] Config validation failed: %s", msg)
        sys.exit(1)

    runner_id = source_config["runner_id"]
    total_episodes = int(source_config["runner_nrof_episodes"])

    log.info("[EXTRACT] Runner ID:        %s", runner_id)
    log.info("[EXTRACT] Total episodes:   %d", total_episodes)
    log.info("[EXTRACT] Extracting:       %d", source_episode)
    log.info("[EXTRACT] Episode sig:      %d", episodesig)

    # ── Step 2: Verify selected episode exists ────────────────────────────
    ep_root = os.path.join(source_dir, "ep")
    persistence_path = os.path.join(ep_root, str(source_episode), f"Persistence-Episode@{source_episode}.json")

    if not os.path.isdir(os.path.join(ep_root, str(source_episode))):
        log.error("[EXTRACT] Source episode directory not found: %s", os.path.join(ep_root, str(source_episode)))
        sys.exit(1)

    ok, data, err = load_json_file(persistence_path)
    if not ok:
        log.error("[EXTRACT] Episode %d persistence unreadable: %s (%s)", source_episode, persistence_path, err)
        sys.exit(1)

    log.info("[EXTRACT] Episode %d verified and readable", source_episode)

    # ── Step 2b: Compute new runner_id with updated alg+runs ───────────────
    new_runner_id = runner_id
    try:
        alg_runs = extract_alg_and_runs(runner_id)
        if alg_runs:
            alg, old_runs = alg_runs
            new_runner_id = replace_alg_runs_in_runner_id(runner_id, alg, old_runs, episodesig)
            log.info("[EXTRACT] Updated runner_id: %s → %s", runner_id, new_runner_id)
        else:
            log.warning("[EXTRACT] Could not extract alg+runs from runner_id, using original: %s", runner_id)
    except ValueError as exc:
        log.error("[EXTRACT] Failed to update runner_id: %s", exc)
        sys.exit(1)

    # ── Step 3: Create target directory structure ─────────────────────────
    target_parent_path = os.path.join(reports_base, target_parent_dir_id)
    target_run_id_path = os.path.join(target_parent_path, "run-id")
    
    # Use new runner_id as the target run_id folder
    target_dir = os.path.join(target_run_id_path, new_runner_id)

    try:
        os.makedirs(target_dir, exist_ok=True)
        os.makedirs(os.path.join(target_dir, "ep"), exist_ok=True)
    except OSError as exc:
        log.error("[EXTRACT] Failed to create target directory: %s", exc)
        sys.exit(1)

    log.info("[EXTRACT] Target: %s", target_dir)

    # ── Step 4: Copy and normalize episode ────────────────────────────────
    ok, msg = normalize_episode_to_one(ep_root, os.path.join(target_dir, "ep"), source_episode)
    if not ok:
        log.error("[EXTRACT] %s", msg)
        sys.exit(1)
    log.info("[EXTRACT] %s", msg)

    # ── Step 5: Create _persistence.json from normalized episode ──────────
    ok, msg = create_persistence_from_episode(os.path.join(target_dir, "ep"), target_dir)
    if not ok:
        log.error("[EXTRACT] %s", msg)
        sys.exit(1)
    log.info("[EXTRACT] %s", msg)

    # ── Step 6: Copy and update config_setting.json ───────────────────────
    try:
        src_config = os.path.join(source_dir, "config_setting.json")
        dst_config = os.path.join(target_dir, "config_setting.json")
        shutil.copy2(src_config, dst_config)
        log.info("[EXTRACT] Copied config_setting.json")
        
        # Update config_setting.json with new runner_id and episode count
        ok, update_msg = update_config_setting_for_extraction(target_dir, new_runner_id, episodesig)
        if not ok:
            log.error("[EXTRACT] %s", update_msg)
            sys.exit(1)
        log.info("[EXTRACT] %s", update_msg)
    except OSError as exc:
        log.error("[EXTRACT] Failed to handle config_setting.json: %s", exc)
        sys.exit(1)

    # ── Step 7: Summary ───────────────────────────────────────────────────
    log.info("%s", "=" * LINE_LENGTH)
    log.info("[EXTRACT] Done!")
    log.info("[EXTRACT] Source directory : %s", source_dir)
    log.info("[EXTRACT] Target directory : %s", target_dir)
    log.info("[EXTRACT] Extracted episode: %d (normalized to episode %d)", source_episode, SAMPLED_INITIAL_EPISODE)
    log.info("[EXTRACT] Output parent ID : %s", target_parent_dir_id)
    log.info("[EXTRACT] New runner_id    : %s", new_runner_id)
    log.info("%s", "=" * LINE_LENGTH)


# ------------------------------------------------------------------------------------------------------------------- #
# CLI ENTRY POINT
# ------------------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Model Extractor — extract a single episode into a fresh run directory for model deployment or analysis."
    )

    parser.add_argument(
        "-pid", "--parent-dir-id", type=str, required=True,
        help="Source parent directory ID under the reports base (e.g. 'skripsi-run1').",
    )

    parser.add_argument(
        "-c", "--config", type=str, required=False,
        help=(
            "Config index filter. Matches run dirs by cfg@N in their name. "
            "Supports comma-separated values and ranges (e.g. '3', '1,2,5', '4-6', '1,3-5,9'). "
            "At least one of -c or -fs must be provided."
        ),
    )

    parser.add_argument(
        "-fs", "--fromsignature", type=str, required=False,
        help=(
            "Source run signature (e.g. 'lfe500'). "
            "Matches run dirs whose folder name contains alg+runs matching this pattern. "
            "At least one of -c or -fs must be provided."
        ),
    )

    parser.add_argument(
        "-oe", "--ofepisode", type=int, required=False,
        help=(
            "Episode number to extract. "
            "If not specified, defaults to the highest available episode."
        ),
    )

    parser.add_argument(
        "-ap", "--aspid", type=str, required=False,
        help=(
            "Output parent directory ID. "
            f"If not specified, defaults to 'sampled-<original_pid>'."
        ),
    )

    parser.add_argument(
        "-srp", "--setreportspath", type=str, required=False,
        help=(
            "Override the base report directory path. "
            "Accepts absolute paths (e.g. 'D:/reports') or relative paths (e.g. 'custom/reports'). "
            f"Default: '{REPORTS_BASE}'"
        ),
    )

    parser.add_argument(
        "-es", "--episodesig", type=int, required=False, default=10,
        help=(
            "Target episode signature (runs count) for the extracted model. "
            "Replaces alg+runs in the runner_id and updates runner_nrof_episodes. "
            "Default: 10"
        ),
    )

    args = parser.parse_args()

    # ── Validate: at least one source filter required ─────────────────────
    if not args.config and not args.fromsignature:
        parser.error("At least one of -c/--config or -fs/--fromsignature must be provided.")

    # ── Resolve reports base ───────────────────────────────────────────────
    reports_base = normalize_report_base(args.setreportspath or REPORTS_BASE)

    # ── Parse config indices (if given) ──────────────────────────────────
    config_indices: Optional[list[int]] = None
    if args.config:
        try:
            config_indices = _parse_config_indices(args.config)
        except ValueError as exc:
            log.error("Invalid -c/--config value: %s", exc)
            sys.exit(1)

        log.info("Config index filter: %s", config_indices)

    # ── Resolve matching source directories ───────────────────────────────
    log.info("%s", "=" * LINE_LENGTH)
    log.info("MODEL EXTRACTOR")
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Source parent ID : %s", args.parent_dir_id)
    log.info("Reports base     : %s", reports_base)
    log.info("From signature   : %s", args.fromsignature or "(not set)")
    log.info("Config filter    : %s", config_indices or "(not set)")
    log.info("Episode to use   : %s", args.ofepisode or "(highest available)")
    log.info("Episode sig      : %d", args.episodesig)
    log.info("Output parent ID : %s", args.aspid or f"sampled-{args.parent_dir_id}")
    log.info("%s", "=" * LINE_LENGTH)

    matched_dirs = None
    try:
        matched_dirs = find_matching_run_dirs(
            args.parent_dir_id,
            reports_base,
            config_indices=config_indices,
            from_signature=args.fromsignature,
        )
    except ValueError as exc:
        log.error("Resolution error: %s", exc)
        sys.exit(1)

    if not matched_dirs:
        log.error("No matching run directories found. Check -pid, -c, and -fs arguments.")
        sys.exit(1)

    log.info("Found %d matching run director%s:", len(matched_dirs), "y" if len(matched_dirs) == 1 else "ies")
    for d in matched_dirs:
        log.info("  %s", d)

    # ── Process each matched directory ───────────────────────────────────
    target_parent_id = args.aspid or f"sampled-{args.parent_dir_id}"

    for source_dir in matched_dirs:
        # Determine episode to extract
        ep_root = os.path.join(source_dir, "ep")
        highest_ep, problems = find_highest_episode(ep_root)

        if problems:
            for p in problems:
                log.warning("[EXTRACT] %s", p)

        if highest_ep <= 0:
            log.error("No valid episodes found in: %s", source_dir)
            sys.exit(1)

        episode_to_extract = args.ofepisode or highest_ep
        
        if episode_to_extract > highest_ep:
            log.error("Requested episode %d exceeds highest available (%d)", episode_to_extract, highest_ep)
            sys.exit(1)

        if episode_to_extract < 1:
            log.error("Episode number must be >= 1")
            sys.exit(1)

        extract_model(
            source_dir=source_dir,
            source_episode=episode_to_extract,
            target_parent_dir_id=target_parent_id,
            reports_base=reports_base,
            episodesig=args.episodesig,
        )

    log.info("%s", "=" * LINE_LENGTH)
    log.info(
        "All done. %d director%s processed.",
        len(matched_dirs),
        "y" if len(matched_dirs) == 1 else "ies",
    )
    log.info("%s", "=" * LINE_LENGTH)

