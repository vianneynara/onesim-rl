"""
episode_extender.py — Episode Extension Setupper

Prepares an existing run directory to continue from where it left off,
extending the total episode count to a new target.

Two resolution modes for the source directory:
  - Signature mode (-fs):  matches run dirs containing alg+runs in their name
  - Config mode    (-c):   matches run dirs by cfg@N pattern (comma/range)

Both modes can be combined: -fs filters by alg+runs AND -c filters by cfg@N.

Usage examples:
  # Extend by signature, copy mode
  python episode_extender.py -pid skripsi-run1 -fs lfe500 --toepisodes 750

  # Extend by config index, overwrite mode
  python episode_extender.py -pid skripsi-run1 -c 3 --toepisodes 750 --overwrite

  # Both filters (must match cfg@03 AND lfe500)
  python episode_extender.py -pid skripsi-run1 -c 3 -fs lfe500 --toepisodes 750

  # Custom reports base path
  python episode_extender.py -pid skripsi-run1 -fs lfe500 --toepisodes 750 -srp D:/reports
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
import time
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

# Default base directory for all report outputs (mirrors batch_runner.py)
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


def find_highest_good_episode(full_report_dir: str) -> Tuple[int, list[str], bool, bool]:
    """
    Determine the highest *contiguous* valid episode number (starting from 1).

    An episode is valid when its Persistence-Episode@N.json is readable JSON.

    Returns:
        (highest_good, problems, episodic_available, main_persistence_available)
        highest_good == 0 when no valid episode exists.
    """
    problems: list[str] = []

    main_persistence = os.path.join(full_report_dir, "_persistence.json")
    if not os.path.isfile(main_persistence):
        problems.append(f"Main persistence missing: {main_persistence} (simulation never ran)")
        return 0, problems, True, False

    ep_root = os.path.join(full_report_dir, "ep")
    if not os.path.isdir(ep_root):
        return 0, [f"Episodic directory missing: {ep_root} (saveEpisodically likely false)"], False, True

    episode_dirs = safe_int_dirnames(ep_root)
    if not episode_dirs:
        problems.append(f"No episode directories found under: {ep_root}")
        return 0, problems, True, True

    highest_good = 0
    for expected in range(1, max(episode_dirs) + 1):
        if expected not in episode_dirs:
            problems.append(f"Missing episode directory: {os.path.join(ep_root, str(expected))}")
            break

        persistence_path = os.path.join(
            ep_root, str(expected), f"Persistence-Episode@{expected}.json"
        )
        ok, data, err = load_json_file(persistence_path)
        if not ok:
            problems.append(f"Episode {expected} unreadable: {persistence_path} ({err})")
            break

        if "episodeNumber" in data:
            try:
                if int(data["episodeNumber"]) != expected:
                    problems.append(
                        f"Episode {expected} mismatch: episodeNumber={data['episodeNumber']}"
                    )
                    break
            except (TypeError, ValueError):
                problems.append(f"Episode {expected} has non-integer episodeNumber")
                break

        highest_good = expected

    return highest_good, problems, True, True


# ------------------------------------------------------------------------------------------------------------------- #
# FOLDER NAMING
# ------------------------------------------------------------------------------------------------------------------- #

def replace_alg_runs_in_runner_id(runner_id: str, alg: str, old_runs: int, new_runs: int) -> str:
    """
    Replace the alg+runs token inside a runner_id string.

    Example:    cfg@03-lfe500-bp@ts  →  cfg@03-lfe750-bp@ts
    Or:         cfg@03-cg@lf-lfe500-bp@ts  →  cfg@03-cg@lf-lfe750-bp@ts
    """
    pattern     = rf"\b{re.escape(alg)}{old_runs}\b"
    replacement = f"{alg}{new_runs}"
    updated     = re.sub(pattern, replacement, runner_id, count=1)

    if updated == runner_id:
        raise ValueError(
            f"Could not find '{alg}{old_runs}' to replace in runner_id: '{runner_id}'"
        )
    return updated


def find_next_version_number(run_id_path: str, base_name: str) -> int:
    """
    Find the next available versioning suffix (N) for a directory named base_name(N).

    Returns 1 when no versioned directory exists yet.
    """
    highest = 0
    for item in os.listdir(run_id_path):
        if item.startswith(base_name + "(") and item.endswith(")"):
            try:
                n = int(item[len(base_name) + 1 : -1])
                highest = max(highest, n)
            except ValueError:
                pass
    return highest + 1


# ------------------------------------------------------------------------------------------------------------------- #
# CONFIG JSON UPDATE
# ------------------------------------------------------------------------------------------------------------------- #

def update_config_setting_json(
        full_report_dir: str,
        new_runner_id: str,
        new_episodes: int,
) -> Tuple[bool, str]:
    """
    Atomically update config_setting.json with the new runner_id and episode count.

    Keys updated:
        runner_id             ← new_runner_id
        runner_nrof_episodes  ← new_episodes

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

        old_episodes  = config.get(good_key, "unknown")
        old_runner_id = config.get("runner_id", "unknown")

        config[good_key]    = new_episodes
        config["runner_id"] = new_runner_id

        highlighted_settings = config.get("highlighted_settings", {})
        overridden_settings = config.get("overridden_settings", [])

        # Reposition highlighted_settings and overridden_settings
        config["highlighted_settings"] = highlighted_settings
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
# COPY HELPERS
# ------------------------------------------------------------------------------------------------------------------- #

def copy_episodes_recursively(
        src_ep_dir: str,
        dst_ep_dir: str,
        max_episode: int,
) -> Tuple[bool, str]:
    """
    Copy ep/1 … ep/max_episode from src to dst, skipping already-existing destinations.

    Returns: (success, message)
    """
    if not os.path.isdir(src_ep_dir):
        return False, f"Source episode directory not found: {src_ep_dir}"

    try:
        os.makedirs(dst_ep_dir, exist_ok=True)
        copied = 0

        for ep in range(1, max_episode + 1):
            src_ep = os.path.join(src_ep_dir, str(ep))
            dst_ep = os.path.join(dst_ep_dir, str(ep))

            if not os.path.isdir(src_ep):
                log.warning("Source episode %d not found — skipping: %s", ep, src_ep)
                continue

            if os.path.exists(dst_ep):
                log.warning("Destination episode %d already exists — skipping: %s", ep, dst_ep)
                continue

            shutil.copytree(src_ep, dst_ep)
            copied += 1

        return True, f"Copied {copied} episode(s) (ep/1 … ep/{max_episode})"
    except Exception as exc:
        return False, f"Failed during episode copy: {exc}"


# ------------------------------------------------------------------------------------------------------------------- #
# MAIN EXTEND LOGIC
# ------------------------------------------------------------------------------------------------------------------- #

def extend_run(
        source_dir: str,
        to_episodes: int,
        overwrite: bool,
        reports_base: str,
        parent_dir_id: str,
        acknowledge_overwrite: bool = False,
) -> None:
    """
    Core extension routine for a single matched source directory.

    Steps:
        1. Validate config_setting.json
        2. Find highest good episode
        3. Compute new runner_id (alg+runs replaced)
        4. OVERWRITE mode: rename source dir in-place
           COPY mode:     copy episodes + config into a new dir
        5. Update config_setting.json in the target directory
    """
    log.info("%s", "=" * LINE_LENGTH)
    log.info("[EXTEND] Source: %s", source_dir)

    # ── Step 1: Validate source config ────────────────────────────────────
    is_valid, msg, source_config = validate_source_config(source_dir)
    if not is_valid:
        log.error("[EXTEND] Config validation failed: %s", msg)
        sys.exit(1)

    old_runner_id = source_config["runner_id"]
    alg           = source_config["runner_algorithm"]
    old_runs      = int(source_config["runner_nrof_episodes"])

    log.info("[EXTEND] Algorithm:        %s", alg)
    log.info("[EXTEND] Current episodes: %d", old_runs)
    log.info("[EXTEND] Target episodes:  %d", to_episodes)
    log.info("[EXTEND] Old runner_id:    %s", old_runner_id)

    # ── Step 2: Find highest good episode ─────────────────────────────────
    highest_good, problems, episodic_available, main_persistence_available = (
        find_highest_good_episode(source_dir)
    )

    if problems:
        for p in problems:
            log.warning("[EXTEND] %s", p)

    log.info("[EXTEND] Highest valid episode: %d", highest_good)

    if highest_good <= 0:
        log.error("[EXTEND] No readable episodes found. Cannot extend.")
        sys.exit(1)

    if to_episodes <= highest_good:
        log.error(
            "[EXTEND] --toepisodes (%d) must be greater than current episode count (%d)",
            to_episodes,
            highest_good,
        )
        sys.exit(1)

    # ── Step 3: Compute new runner_id ────────────────────────────────────
    try:
        new_runner_id = replace_alg_runs_in_runner_id(old_runner_id, alg, old_runs, to_episodes)
    except ValueError as exc:
        log.error("[EXTEND] %s", exc)
        sys.exit(1)

    log.info("[EXTEND] New runner_id: %s", new_runner_id)

    source_parent = os.path.dirname(source_dir)   # …/reports_base/parent_dir_id/run-id
    run_id_path   = source_parent                  # same thing, clearer alias

    # ── Step 4a: OVERWRITE (rename) mode ──────────────────────────────────
    if overwrite:
        target_runner_id = new_runner_id
        target_dir       = os.path.join(run_id_path, target_runner_id)

        # Collision guard: if a *different* dir with the new name already exists
        if os.path.exists(target_dir) and os.path.abspath(target_dir) != os.path.abspath(source_dir):
            version_num      = find_next_version_number(run_id_path, target_runner_id)
            target_runner_id = f"{target_runner_id}({version_num})"
            target_dir       = os.path.join(run_id_path, target_runner_id)
            log.warning("[EXTEND] Target name collision — using versioned name: %s", target_runner_id)

        log.info("[EXTEND] Mode: OVERWRITE (rename in-place)")
        log.info("[EXTEND] Renaming: %s → %s", os.path.basename(source_dir), target_runner_id)

        if os.path.abspath(source_dir) != os.path.abspath(target_dir):
            os.rename(source_dir, target_dir)
            log.info("[EXTEND] Rename complete")

    # ── Step 4b: COPY mode ───────────────────────────────────────────────
    else:
        target_runner_id = new_runner_id
        target_dir       = os.path.join(run_id_path, target_runner_id)

        # Collision guard
        if os.path.exists(target_dir):
            version_num      = find_next_version_number(run_id_path, target_runner_id)
            target_runner_id = f"{target_runner_id}({version_num})"
            target_dir       = os.path.join(run_id_path, target_runner_id)
            log.warning("[EXTEND] Target name collision — using versioned name: %s", target_runner_id)

        if not acknowledge_overwrite:
            WAIT_TIME = 10
            log.info("⚠️" * (LINE_LENGTH // 2))
            log.info("[EXTEND] Mode: COPY")
            log.info("[EXTEND] Copying ep/1 … ep/%d", highest_good)
            log.info("[EXTEND] Source : %s", source_dir)
            log.info("[EXTEND] Target : %s", target_dir)
            log.info("[EXTEND] Continuing in %d seconds. Ctrl+C to cancel.", WAIT_TIME)
            log.info("⚠️" * (LINE_LENGTH // 2))
            time.sleep(WAIT_TIME)

        os.makedirs(target_dir, exist_ok=True)

        # Copy episodes
        ok, copy_msg = copy_episodes_recursively(
            os.path.join(source_dir, "ep"),
            os.path.join(target_dir, "ep"),
            highest_good,
        )
        if not ok:
            log.error("[EXTEND] Episode copy failed: %s", copy_msg)
            sys.exit(1)
        log.info("[EXTEND] %s", copy_msg)

        # Copy config_setting.json
        shutil.copy2(
            os.path.join(source_dir, "config_setting.json"),
            os.path.join(target_dir, "config_setting.json"),
        )
        log.info("[EXTEND] Copied config_setting.json")

        # Copy _persistence.json if present
        src_persistence = os.path.join(source_dir, "_persistence.json")
        if os.path.isfile(src_persistence):
            shutil.copy2(src_persistence, os.path.join(target_dir, "_persistence.json"))
            log.info("[EXTEND] Copied _persistence.json")

    # ── Step 5: Update config_setting.json in target ──────────────────────
    ok, update_msg = update_config_setting_json(target_dir, target_runner_id, to_episodes)
    if not ok:
        log.error("[EXTEND] Failed to update config_setting.json: %s", update_msg)
        sys.exit(1)

    log.info("[EXTEND] %s", update_msg)
    log.info("%s", "=" * LINE_LENGTH)
    log.info("[EXTEND] Done!")
    log.info("[EXTEND] Target directory : %s", target_dir)
    log.info("[EXTEND] Episodes to run  : %d → %d (new episodes: %d)", highest_good + 1, to_episodes, to_episodes - highest_good)
    log.info("%s", "=" * LINE_LENGTH)


# ------------------------------------------------------------------------------------------------------------------- #
# CLI ENTRY POINT
# ------------------------------------------------------------------------------------------------------------------- #

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Episode Extension Setupper — prepares a run directory to continue to a higher episode count."
    )

    parser.add_argument(
        "-pid", "--parent-dir-id", type=str, required=True,
        help="Parent directory ID under the reports base (e.g. 'skripsi-run1').",
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
        "--toepisodes", type=int, required=True,
        help="Target total episode count. Must be greater than the current highest valid episode.",
    )

    parser.add_argument(
        "--overwrite", action="store_true",
        help=(
            "Extend in-place: rename the source directory instead of copying it. "
            "Modifies config_setting.json inside the renamed directory."
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
        "-ack", "--acknowledge", action="store_true", required=False,
        help="Acknowledge and bypass override extend, automatically ignoring the warning.",
    )

    args = parser.parse_args()

    # ── Validate: at least one source filter required ─────────────────────
    if not args.config and not args.fromsignature:
        parser.error("At least one of -c/--config or -fs/--fromsignature must be provided.")

    if args.toepisodes <= 0:
        parser.error("--toepisodes must be a positive integer.")

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
    log.info("EPISODE EXTENDER")
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Parent dir ID    : %s", args.parent_dir_id)
    log.info("Reports base     : %s", reports_base)
    log.info("From signature   : %s", args.fromsignature or "(not set)")
    log.info("Config filter    : %s", config_indices or "(not set)")
    log.info("To episodes      : %d", args.toepisodes)
    log.info("Overwrite mode   : %s", "YES" if args.overwrite else "NO (copy)")
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

    # ── Extend each matched directory ────────────────────────────────────
    if len(matched_dirs) > 1:
        MULTI_WAIT = 10
        log.info("⚠️" * (LINE_LENGTH // 2))
        log.info("Multiple directories will be extended. Continuing in %d seconds. Ctrl+C to cancel.", MULTI_WAIT)
        log.info("⚠️" * (LINE_LENGTH // 2))
        time.sleep(MULTI_WAIT)

    for source_dir in matched_dirs:
        extend_run(
            source_dir=source_dir,
            to_episodes=args.toepisodes,
            overwrite=args.overwrite,
            reports_base=reports_base,
            parent_dir_id=args.parent_dir_id,
            acknowledge_overwrite=args.acknowledge,
        )

    log.info("%s", "=" * LINE_LENGTH)
    log.info("All done. %d director%s extended.", len(matched_dirs), "y" if len(matched_dirs) == 1 else "ies")
    log.info("%s", "=" * LINE_LENGTH)