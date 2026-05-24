"""
The second version of batch runner, will provide better and more flexible runs.
"""

# ------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------------------------------------------- #

import argparse
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Any

# Allow running this file as a script (python pyrunner/batch_runner.py) while still
# using absolute package imports (pyrunner.*).
#
# Important: this must run *before* importing pyrunner.*
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.term_dictionary import KEY_ABBREVIATIONS, BEHAVIOR_PACKAGES, ALG_BASE_SETTINGS_PATH, ALG_ABBREVIATIONS
from pyrunner.config_parser import parse_config_file, extract_highlighted_settings
from pyrunner.utils.fs import safe_int_dirnames
from pyrunner.utils.jsonio import load_json_file
from pyrunner.utils.path import validate_run_id, normalize_report_base
from pyrunner.utils.timefmt import format_timedelta

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------------------------------------------- #
# BATCH RUNNER CONFIGURATION
# ------------------------------------------------------------------------------------------------------------------- #

# Default base directory for all report outputs
REPORTS_BASE = "reports/skripsi"

ID_LABEL = "ID_LABEL"
ALG_LABEL = "ALG_LABEL"

S_REPORT_DIR = f"Report.reportDir={REPORTS_BASE}/{ALG_LABEL}/run-id/{ID_LABEL}"

PRIORITY_OVERRIDE_KEYS = ["lfe_la", "qlm_bp", "mcnm_bp"]

# Import the configs
from pyrunner.batch_configs import LIST_OF_CONFIGS
# from pyrunner.batch_configs_jord import LIST_OF_CONFIGS

HIGHLIGHTED_SETTINGS = [
    "MovementModel.rngSeed",
    "MovementModel.worldSize",

    "StationaryClustered.alpha",
    "StationaryClustered.cluster",
    "StationaryClustered.sigma",

    "QLearningMovement.learningRate",
    "QLearningMovement.discountFactor",
    "QLearningMovement.initialQValue",
    "QLearningMovement.targetPrefix",
    "QLearningMovement.stepPenalty",
    "QLearningMovement.foundReward",
    "QLearningMovement.agentSpeed",
    "QLearningMovement.targetCooldown",
    "QLearningMovement.learningSeed",

    "MCMovementEnd.learningRate",
    "MCMovementEnd.discountFactor",
    "MCMovementEnd.initialQValue",
    "MCMovementEnd.behaviorPolicy",
    "MCMovementEnd.targetPrefix",
    "MCMovementEnd.stepPenalty",
    "MCMovementEnd.foundReward",
    "MCMovementEnd.agentSpeed",
    "MCMovementEnd.targetCooldown",
    "MCMovementEnd.learningSeed",
    "MCMovementEnd.firstVisit",

    "LevyFlightEpisodic.levyAlpha",
    "LevyFlightEpisodic.xm",
    "LevyFlightEpisodic.targetPrefix",
    "LevyFlightEpisodic.flightSpeed",
    "LevyFlightEpisodic.targetCooldown",
    "LevyFlightEpisodic.stepPenalty",
    "LevyFlightEpisodic.foundReward",
    "LevyFlightEpisodic.learningSeed",

    "BehaviorPolicy.EpsilonGreedy.epsilon",
    "BehaviorPolicy.EpsilonGreedy.epsilonDecay",
    "BehaviorPolicy.EpsilonGreedy.minEpsilon",

    "BehaviorPolicy.UCB.explorationConstant",

    "BehaviorPolicy.PS.initialVariance",

    "SearchingAgentRouter.targetPrefix",
    "Group1.nrofHosts",
    "Group1.movementModel",
    "Group2.nrofHosts",
    "Group2.movementModel",
    "Group2.groupID",
]


def create_config_setting_json(
        alg: str,
        parent_dir_id: str,
        runs: int,
        bp: Optional[str],
        result_dir_id: str = None,
        overrides_list: list[str] = None,
        custom_cfg: Optional[str] = None,
        alg_override: Optional[str] = None,
        reports_base: str = REPORTS_BASE
):
    # Parse the algorithm's base config file (or custom config if provided)
    cfg_file_path = expand_algorithm(alg, custom_cfg, alg_override)
    config_dict = parse_config_file(cfg_file_path)
    
    # Extract highlighted settings from the parsed config
    _highlighted_settings = extract_highlighted_settings(config_dict, HIGHLIGHTED_SETTINGS)
    
    # Initialize overridden settings with algorithm mapping
    _overridden_settings = {
        "amm": ALG_ABBREVIATIONS[alg],
    }

    # Build config setting JSON
    config_setting_json = {
        "parent_dir_id": parent_dir_id,
        "runner_id": result_dir_id,
        "runner_algorithm": alg,
        "runner_nrof_episodes": runs,
    }

    # Add behavior policy override if specified
    bp_key = _get_bp_override_key(alg)
    if bp and bp_key:
        _overridden_settings[bp_key] = BEHAVIOR_PACKAGES[bp]

    # Process additional overrides from the override list
    for entry in overrides_list or []:
        key, value = entry.split("=", 1)
        _overridden_settings[key] = value

    # Merge settings: overridden_settings take precedence over highlighted_settings
    _highlighted_settings.update(_overridden_settings)
    
    # Add merged settings to config JSON
    config_setting_json["highlighted_settings"] = _highlighted_settings
    config_setting_json["overridden_settings"] = _overridden_settings

    # Create the directory first using reports_base
    dir_path = os.path.join(reports_base, parent_dir_id, "run-id", result_dir_id)
    os.makedirs(dir_path, exist_ok=True)

    # Save the JSON to the report directory
    with open(os.path.join(dir_path, "config_setting.json"), "w") as json_file:
        json.dump(config_setting_json, json_file, indent=4)


def parse_overrides(overrides_dict: dict[str, Any]) -> Tuple[list[str], list[str]]:
    # convert the override dictionary into a list of key-value
    abr_overrides_list = []
    full_overrides_list = []
    for key, value in overrides_dict.items():

        # Check if key is an abbreviation
        if key in KEY_ABBREVIATIONS:
            full_key = KEY_ABBREVIATIONS[key]
        else:
            # Use the key as-is (assuming the real setting full key)
            full_key = key

        abr_overrides_list.append(f"{key}@{value}")
        full_overrides_list.append(f"{full_key}={value}")

    return abr_overrides_list, full_overrides_list


def _get_bp_override_key(alg: str) -> Optional[str]:
    if alg == "ql":
        return "qlm_bp"
    if alg == "mcn":
        return "mcnm_bp"
    return None


def _order_abbreviated_overrides(abr_overrides: list[str]) -> list[str]:
    if not abr_overrides:
        return []

    priority = []
    remainder = []
    for entry in abr_overrides:
        key = entry.split("@", 1)[0]
        if key in PRIORITY_OVERRIDE_KEYS:
            priority.append(entry)
        else:
            remainder.append(entry)

    ordered = []
    for key in PRIORITY_OVERRIDE_KEYS:
        ordered.extend([item for item in priority if item.startswith(f"{key}@")])
    ordered.extend(remainder)
    return ordered


def expand_algorithm(alg: str, custom_cfg: Optional[str] = None, alg_override: Optional[str] = None) -> str:
    """
    Resolve the config file path for an algorithm.
    
    Precedence (highest to lowest):
    1. custom_cfg: Direct custom config file path (e.g., "custom-setting.cfg" or "settings/skripsi/custom-setting.cfg")
    2. alg_override: Algorithm key from ALG_BASE_SETTINGS_PATH (e.g., "ql", "mc", "lfe")
    3. alg: Default algorithm parameter
    """
    if custom_cfg:
        # Use custom config file, ensuring it follows the same root directory structure
        # Expected format: e.g., "custom-setting.cfg" or full path "settings/skripsi/custom-setting.cfg"
        if custom_cfg.startswith("settings/skripsi/"):
            return custom_cfg
        else:
            return f"settings/skripsi/{custom_cfg}"
    
    if alg_override:
        # Use algorithm override key to look up config from ALG_BASE_SETTINGS_PATH
        if alg_override not in ALG_BASE_SETTINGS_PATH:
            raise ValueError(
                f"Unknown algorithm override '{alg_override}'. Valid options: {', '.join(ALG_BASE_SETTINGS_PATH.keys())}"
            )
        return ALG_BASE_SETTINGS_PATH[alg_override]
    
    if alg not in ALG_BASE_SETTINGS_PATH:
        raise ValueError(
            f"Unknown algorithm '{alg}'. Valid options: {', '.join(ALG_BASE_SETTINGS_PATH.keys())}"
        )
    return ALG_BASE_SETTINGS_PATH[alg]


def build_result_id_dir(
        alg: str,
        runs: int,
        config_index: int,
        overrides: list[str],
        run_id: Optional[str],
        group: Optional[str] = None
) -> str:
    prefix = f"cfg@{config_index:02}"
    
    # Insert group right after cfg@N prefix, before alg+runs
    if group:
        prefix = f"{prefix}-cg@{group}"
    
    prefix = f"{prefix}-{alg}{runs}"
    ordered_overrides = _order_abbreviated_overrides(overrides)

    if ordered_overrides:
        suffix = "-".join(ordered_overrides)
    else:
        suffix = run_id or ""

    return f"{prefix}-{suffix}" if suffix else prefix


def run_script(algo: str, overrides_string: str = None, ep: int = -1, custom_cfg: Optional[str] = None, alg_override: Optional[str] = None) -> bool:
    script = [
        r".\one.bat",
        "-b",
        "1",
    ]

    # Add overrides only if provided
    if overrides_string:
        script.extend(["-d", overrides_string])

    # Add config file path (custom config, algorithm override, or default)
    script.append(expand_algorithm(algo, custom_cfg, alg_override))

    _start_time = None
    _end_time = None

    try:
        _start_time = datetime.now()

        log.info("%s", "-" * LINE_LENGTH)
        log.info("Running episode %s for algorithm %s.", ep, algo)
        log.info("%s", "-" * LINE_LENGTH)
        log.info("Running command: %s", " ".join(script))
        result = subprocess.run(script, shell=True)
        
        if result.returncode != 0:
            log.error("Episode %s failed with exit code: %s", ep, result.returncode)
            return False
        
        return True
    except Exception as e:
        log.error("Exception while running episode %s for algorithm %s: %s", ep, algo, e)
        return False
    finally:
        _end_time = datetime.now()

        if _start_time is not None:
            took = format_timedelta(_end_time - _start_time)
        else:
            took = "??:??:??"
        log.info("%s", "-" * LINE_LENGTH)
        log.info("Done running episode %s for algorithm %s. Took %s.", ep, algo, took)
        log.info("%s", "-" * LINE_LENGTH)


def find_next_version_number(parent_dir_id: str, base_result_id_dir: str, reports_base: str = REPORTS_BASE) -> int:
    """
    Find the next available version number for a run directory.
    
    Checks if base_result_id_dir exists, and if so, finds the highest version number (N) where
    base_result_id_dir(N) exists, then returns N+1. If base_result_id_dir doesn't exist, returns 1.
    
    Args:
        parent_dir_id: Parent directory identifier
        base_result_id_dir: Base result directory name
        reports_base: Base reports directory path
    
    Returns: Next version number (1-based, or 1 if no versioned directory exists yet)
    """
    base_path = os.path.join(reports_base, parent_dir_id, "run-id", base_result_id_dir)

    # If base directory doesn't exist yet, no versioning needed
    if not os.path.isdir(base_path):
        return 1

    # Base directory exists; find the highest version number
    highest_version = 0

    # Check for versioned directories (N) in parent
    parent_path = os.path.dirname(base_path)
    if not os.path.isdir(parent_path):
        return 1

    for item in os.listdir(parent_path):
        item_path = os.path.join(parent_path, item)
        if not os.path.isdir(item_path):
            continue

        # Check if this item matches the pattern: base_result_id_dir(N)
        if item.startswith(base_result_id_dir + "(") and item.endswith(")"):
            try:
                version_str = item[len(base_result_id_dir) + 1:-1]
                version_num = int(version_str)
                highest_version = max(highest_version, version_num)
            except (ValueError, IndexError):
                pass

    # Also check if unversioned base directory exists
    if os.path.isdir(base_path):
        highest_version = max(highest_version, 0)

    return highest_version + 1


def get_versioned_result_id_dir(parent_dir_id: str, base_result_id_dir: str, reports_base: str = REPORTS_BASE) -> str:
    """
    Get the versioned result_id_dir if needed.
    
    If the base result_id_dir directory doesn't exist, returns it as-is.
    If it exists, appends (N) where N is the next available version number.
    
    Args:
        parent_dir_id: Parent directory identifier
        base_result_id_dir: Base result directory name
        reports_base: Base reports directory path
    
    Returns: result_id_dir, possibly with (N) suffix
    """
    base_path = os.path.join(reports_base, parent_dir_id, "run-id", base_result_id_dir)

    if not os.path.isdir(base_path):
        # No existing run, use base as-is
        return base_result_id_dir

    # Existing run detected, find next version
    next_version = find_next_version_number(parent_dir_id, base_result_id_dir, reports_base)
    versioned_id = f"{base_result_id_dir}({next_version})"

    WAIT_TIME = 10

    log.info("⚠️" * (LINE_LENGTH // 2))
    log.info(
        "[OVERRIDE] Existing run detected at: %s",
        base_path
    )
    log.info(
        "[OVERRIDE] Creating versioned run: %s",
        versioned_id
    )

    log.info("[OVERRIDE] Continuing running in %s seconds. \"Ctrl + C\" to cancel.", WAIT_TIME)
    log.info("⚠️" * (LINE_LENGTH // 2))
    time.sleep(WAIT_TIME)  # Making sure the user reads this

    return versioned_id


def find_highest_good_episode(full_report_dir: str) -> Tuple[int, list[str], bool, bool]:
    """Determine highest *contiguous* episode number (starting from 1) in which Persistence-Episode@N.json is readable JSON.
    
    Falls back to episode 0 if no contiguous training episodes (1+) exist.

    Returns: (highest_good, problems, episodic_available, main_persistence_available)
    - highest_good is 0 if no training episodes exist (but episode 0 baseline may be available).
    - episodic_available False means ep/ directory missing (saveEpisodically likely false).
    - main_persistence_available False means _persistence.json missing (simulation has never run).
    """
    problems: list[str] = []

    # Check main persistence file first (adjacent to config_setting.json)
    main_persistence_path = os.path.join(full_report_dir, "_persistence.json")
    main_persistence_available = os.path.isfile(main_persistence_path)
    if not main_persistence_available:
        problems.append(f"Main persistence not found: {main_persistence_path} (simulation has never run)")
        return 0, problems, True, False

    ep_root = os.path.join(full_report_dir, "ep")
    if not os.path.isdir(ep_root):
        return 0, [f"Episodic directory not found: {ep_root} (saveEpisodically likely false)"], False, True

    episode_dirs = safe_int_dirnames(ep_root)
    if not episode_dirs:
        problems.append(f"No episode directories found under: {ep_root}")
        return 0, problems, True, True

    highest_good = 0
    # Contiguous check from 1... until first failure
    for expected in range(1, max(episode_dirs) + 1):
        if expected not in episode_dirs:
            problems.append(f"Missing episode directory: {os.path.join(ep_root, str(expected))}")
            break

        persistence_path = os.path.join(ep_root, str(expected), f"Persistence-Episode@{expected}.json")
        ok, data, err = load_json_file(persistence_path)
        if not ok:
            problems.append(f"Episode {expected} persistence unreadable: {persistence_path} ({err})")
            break

        # If episodeNumber exists, ensure the stored Persistence JSON data matches
        if "episodeNumber" in data:
            try:
                if int(data["episodeNumber"]) != expected:
                    problems.append(
                        f"Episode {expected} persistence mismatch: episodeNumber={data['episodeNumber']} in {persistence_path}"
                    )
                    break
            except (TypeError, ValueError):
                problems.append(f"Episode {expected} persistence has non-integer episodeNumber in {persistence_path}")
                break

        highest_good = expected

    # If no training episodes found, fall back to episode 0 if available
    if highest_good == 0 and 0 in episode_dirs:
        persistence_path = os.path.join(ep_root, "0", "Persistence-Episode@0.json")
        ok, data, err = load_json_file(persistence_path)
        if ok:
            # Validate episodeNumber field if present
            if "episodeNumber" in data:
                try:
                    if int(data["episodeNumber"]) == 0:
                        # Episode 0 is valid as a baseline
                        pass
                    else:
                        problems.append(
                            f"Episode 0 persistence mismatch: episodeNumber={data['episodeNumber']} in {persistence_path}"
                        )
                        return 0, problems, True, True
                except (TypeError, ValueError):
                    problems.append(f"Episode 0 persistence has non-integer episodeNumber in {persistence_path}")
                    return 0, problems, True, True
            # Episode 0 is available as baseline; highest_good stays 0, but no error
        else:
            problems.append(f"Episode 0 persistence unreadable: {persistence_path} ({err})")

    return highest_good, problems, True, True


def rebuild_main_persistence_from_episode(full_report_dir: str, episode: int) -> Tuple[bool, str]:
    """Rebuild {full_report_dir}/_persistence.json from ep/{episode}/Persistence-Episode@{episode}.json."""
    src = os.path.join(full_report_dir, "ep", str(episode), f"Persistence-Episode@{episode}.json")
    dst = os.path.join(full_report_dir, "_persistence.json")
    tmp = dst + ".tmp"

    ok, data, err = load_json_file(src)
    if not ok:
        return False, f"Cannot rebuild _persistence.json; source unreadable: {src} ({err})"

    try:
        os.makedirs(full_report_dir, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, sort_keys=True)
        os.replace(tmp, dst)
        return True, f"Rebuilt _persistence.json from episode {episode}: {dst}"
    except OSError as e:
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except OSError:
            pass
        return False, f"Failed to write/replace persistence file: {e}"


def run_simulation(
        alg: str,
        runs: int,
        config_index: int,
        bp: Optional[str] = None,
        run_id: Optional[str] = None,
        overrides_list: Optional[dict[str, Any]] = None,
        group: Optional[str] = None,
        verify: bool = False,
        do_continue: bool = False,
        parent_dir_id: Optional[str] = None,
        custom_cfg: Optional[str] = None,
        alg_override: Optional[str] = None,
        report_base: str = REPORTS_BASE,
        continue_on_error: bool = False
) -> bool:
    # Validate algorithm
    settings_file = expand_algorithm(alg, custom_cfg, alg_override)

    # Normalize report_base (handles both absolute and relative paths)
    normalized_report_base = normalize_report_base(report_base)

    # Validate behavior policy if provided
    if bp and bp not in BEHAVIOR_PACKAGES:
        raise ValueError(
            f"Unknown behavior policy '{bp}'. Valid options: {', '.join(BEHAVIOR_PACKAGES.keys())}"
        )

    abr_overrides, full_overrides = [], []

    # Build the base overrides
    if overrides_list:
        abr_overrides, full_overrides = parse_overrides(overrides_list)

    bp_override_key = _get_bp_override_key(alg)
    if bp and bp_override_key:
        bp_entry_exists = overrides_list and bp_override_key in overrides_list
        if not bp_entry_exists:
            abr_overrides.append(f"{bp_override_key}@{bp}")
            full_overrides.append(f"{KEY_ABBREVIATIONS[bp_override_key]}={BEHAVIOR_PACKAGES[bp]}")

    result_id_dir = build_result_id_dir(alg, runs, config_index, abr_overrides, run_id, group)
    validate_run_id(result_id_dir)

    # Allow overriding the {alg} portion of the report path
    parent_dir_id_effective = (parent_dir_id or alg).strip()
    validate_run_id(parent_dir_id_effective)

    # Check if we need versioning (only when NOT in verify or continue mode)
    if not verify and not do_continue:
        result_id_dir = get_versioned_result_id_dir(parent_dir_id_effective, result_id_dir, normalized_report_base)

    full_report_dir = os.path.join(normalized_report_base, parent_dir_id_effective, "run-id", result_id_dir)

    persistence_override = f"EpisodicPersistenceManager.persistencePath={full_report_dir}/_persistence.json"
    full_overrides.append(persistence_override)

    overrides_string = "@@".join(full_overrides) if full_overrides else None

    # Print run information
    log.info("%s", "=" * LINE_LENGTH)
    log.info("Starting episodic simulation batch...")
    log.info("Algorithm: %s (%s), Behavior Policy: %s", alg, settings_file, bp)
    log.info("Run ID: %s, Number of episodes: %s", run_id, runs)
    log.info(
        "Report parent dir id: %s (under base: %s)",
        parent_dir_id_effective,
        normalized_report_base,
    )
    log.info("Overrides: %s", overrides_string if overrides_string else "None")
    log.info("%s", "=" * LINE_LENGTH)

    # Create a JSON to log the current running simulation configuration
    create_config_setting_json(alg, parent_dir_id_effective, runs, bp, result_id_dir, full_overrides, custom_cfg, alg_override, normalized_report_base)

    # Verification / continue pre-flight
    start_ep = 1
    highest_good = 0
    episodic_available = True
    main_persistence_available = True
    if verify or do_continue:
        highest_good, problems, episodic_available, main_persistence_available = find_highest_good_episode(
            full_report_dir)
        expected_last = runs

        log.info("%s", "-" * LINE_LENGTH)
        log.info("[VERIFY] Run dir: %s", full_report_dir)
        log.info("[VERIFY] Expected episodes (runs): %s", expected_last)
        log.info("[VERIFY] Main persistence available: %s", main_persistence_available)
        log.info("[VERIFY] Highest contiguous uncorrupted episode: %s", highest_good)
        if problems:
            for p in problems:
                log.warning("[VERIFY] %s", p)
        if main_persistence_available:
            if episodic_available:
                if highest_good >= expected_last:
                    log.info("[VERIFY] Complete (%s/%s)", highest_good, expected_last)
                else:
                    log.warning("[VERIFY] Incomplete (%s/%s)", highest_good, expected_last)
            else:
                log.warning("[VERIFY] Cannot verify episodic persistence (saveEpisodically likely false).")
        else:
            log.warning("[VERIFY] Main persistence missing; simulation has never run. Will start from episode 1.")
        log.info("%s", "-" * LINE_LENGTH)

        if not episodic_available and main_persistence_available:
            log.error("[VERIFY] Episodic snapshots missing. Exiting with error code 1.")
            return False

        if do_continue:
            if not main_persistence_available:
                log.warning(
                    "[CONTINUE] Main persistence not available; simulation has never run. Will restart from episode 1."
                )
                start_ep = 1
            elif not episodic_available:
                # Per requirement: restart from 0 (effectively episode 1), but print warning and highest uncorrupted episode.
                log.warning(
                    "[CONTINUE] Episodic snapshots not available; cannot rebuild from ep/N. Will restart from episode 1."
                )
                start_ep = 1
            elif highest_good < 0:
                log.warning("[CONTINUE] No readable episodic snapshot found; will restart from episode 1.")
                start_ep = 1
            elif highest_good == 0:
                # Check if episode 0 (baseline) exists as fallback
                ep_0_path = os.path.join(full_report_dir, "ep", "0", "Persistence-Episode@0.json")
                if os.path.isfile(ep_0_path):
                    ok, msg = rebuild_main_persistence_from_episode(full_report_dir, 0)
                    if ok:
                        log.info("[CONTINUE] %s", msg)
                    else:
                        log.warning("[CONTINUE] %s", msg)
                    start_ep = 1
                    log.info(
                        "[CONTINUE] No training episodes found; using episode 0 as baseline. Resuming from episode 1."
                    )
                else:
                    log.warning("[CONTINUE] No training episodes and no episode 0 baseline found; will restart from episode 1.")
                    start_ep = 1
            else:
                # highest_good > 0: Rebuild main persistence from last good, then resume from the next episode.
                # Assumption: if Persistence-Episode@K.json exists and is readable, K is uncorrupted.
                ok, msg = rebuild_main_persistence_from_episode(full_report_dir, highest_good)
                if ok:
                    log.info("[CONTINUE] %s", msg)
                else:
                    log.warning("[CONTINUE] %s", msg)

                start_ep = highest_good + 1
                if start_ep > runs:
                    log.info("[CONTINUE] Already complete (%s/%s). Nothing to continue.", highest_good, runs)
                    return True

            if highest_good > 0 and start_ep <= runs:
                log.info(
                    "[CONTINUE] Highest uncorrupted episode: %s. Resuming from episode %s (next episode).",
                    highest_good,
                    start_ep,
                )

    # If only verifying, do not run anything.
    if verify and not do_continue:
        return highest_good >= runs

    # Execute episodes
    succeeds = 0
    failed = 0
    start_time = datetime.now()

    for ep in range(start_ep, runs + 1):
        ep_overrides = list(full_overrides)
        ep_overrides.append(f"Report.reportDir={full_report_dir}/ep/{str(ep)}")
        ep_overrides.append(f"EpisodicPersistenceManager.episodeNumber={str(ep)}")
        running_overrides_string = "@@".join(ep_overrides)
        if run_script(alg, running_overrides_string, ep, custom_cfg, alg_override):
            succeeds += 1
        else:
            failed += 1
            # Stop on first error unless continue_on_error is True
            if not continue_on_error:
                log.warning(
                    "Episode %s failed. Stopping config run (use --continue-on-error to override).",
                    ep
                )
                break

    end_time = datetime.now()

    # Print summary
    log.info("%s", "=" * LINE_LENGTH)
    log.info(
        "Episodic simulation batch completed at %s, time taken: %s",
        end_time,
        format_timedelta(end_time - start_time),
    )
    log.info("Total episodes: %s (Success: %s, Fails: %s)", runs, succeeds, failed)
    log.info("%s", "=" * LINE_LENGTH)

    return failed == 0


def check_runs(args_runs: int, config: dict[str, Any] = None) -> int:
    _runs = 0
    if args_runs:
        if args_runs <= 0:
            log.error("Invalid number of runs: %s", args_runs)
            sys.exit(1)
        _runs = args_runs
    else:
        if not config["runs"]:
            log.error("No number of runs specified in config: %s", str(config["id"]))
            sys.exit(1)
        if config["runs"] and config["runs"] <= 0:
            log.error("Invalid number of runs in config: %s", str(config["runs"]))
            sys.exit(1)
        else:
            _runs = config["runs"]

    return _runs


def parse_config_indices(config_string: str) -> list[int]:
    """
    Parse config indices from a string supporting:
    - Single values: "1,2,9"
    - Ranges: "4-6" (expands to 4,5,6)
    - Mixed: "1,2,4-6,9,10-17"
    """
    configs = set()

    # Split by comma
    parts = config_string.split(",")

    for part in parts:
        part = part.strip()  # Remove whitespace

        if "-" in part:
            # It's a range
            try:
                start_str, end_str = part.split("-", 1)  # Use maxsplit=1 to handle negative numbers
                start = int(start_str.strip())
                end = int(end_str.strip())

                if start > end:
                    raise ValueError(f"Warning: Invalid range '{part}', start > end. Skipping.")

                # Add all values in range (inclusive)
                for i in range(start, end + 1):
                    configs.add(i)
            except ValueError:
                raise ValueError(f"Warning: Invalid range format '{part}'. Skipping.")
        else:
            # It's a single value
            try:
                configs.add(int(part))
            except ValueError:
                raise ValueError(f"Warning: Invalid config number '{part}'. Skipping.")

    return sorted(list(configs))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ONE Simulator multi-run/episodic launcher (version 2), simpler"
    )

    parser.add_argument(
        "-c", "--config", type=str, help="Config index to run", required=False
    )

    parser.add_argument(
        "-a", "--all", action="store_true", help="Run all configs"
    )

    parser.add_argument(
        "-r", "--runs", type=int, help="Number of runs for the simulation (overrides the existing configs)",
        required=False
    )

    parser.add_argument(
        "-cc", "--count-configs", action="store_true",
        help="Count the number of configs in the LIST_OF_CONFIGS and exit"
    )

    parser.add_argument(
        "-pid", "--parent-dir-id", type=str, required=False,
        help="Override script report dir base folder name under report base directory. Default uses algorithm key (e.g., 'ql')."
    )

    parser.add_argument(
        "-srp", "--setreportspath", type=str, required=False,
        help="Override base report directory path. Accepts absolute paths (e.g., 'D:/test/newdir') or relative paths from current working directory (e.g., 'custom/reports'). Default: 'reports/skripsi'"
    )

    parser.add_argument(
        "-alg", "--algorithm", type=str, required=False,
        help=f"Override algorithm config file using ALG_BASE_SETTINGS_PATH key (e.g., {', '.join(ALG_BASE_SETTINGS_PATH.keys())}). Lower priority than --runcfg."
    )

    parser.add_argument(
        "-rcfg", "--runcfg", type=str, required=False,
        help="Override the algorithm-based config file with a custom config file path (e.g., 'custom-setting.cfg' or 'settings/skripsi/custom-setting.cfg'). Uses the same root directory (settings/skripsi/) if only filename is provided. Takes precedence over --alg."
    )

    parser.add_argument(
        "--verify", action="store_true",
        help="Verify that selected configurations have complete, uncorrupted episodic persistence up to their runs"
    )

    parser.add_argument(
        "--continue", dest="do_continue", action="store_true",
        help="Verify and continue from the last good episode by rebuilding _persistence.json from it"
    )

    parser.add_argument(
        "-vc", action="store_true",
        help="Shortcut for --verify --continue"
    )

    parser.add_argument(
        "--continue-on-error", action="store_true",
        help="Continue running remaining episodes even if one fails. Default behavior is to stop on first error."
    )

    # Parse arguments
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    # -vc is equivalent to --verify --continue
    if getattr(args, "vc", False):
        args.verify = True
        args.do_continue = True

    if args.count_configs:
        log.info("Number of configs: %s", len(LIST_OF_CONFIGS))
        sys.exit(0)

    successes = 0
    failures = 0

    start_time = datetime.now()
    running_times = []

    if args.all:
        log.info("Running %s configurations.", len(LIST_OF_CONFIGS))
        for config in LIST_OF_CONFIGS:
            alg = config["alg"]

            runs = check_runs(args.runs, config)

            bp = config["bp"] if "bp" in config else None
            id = config["id"]
            group = config.get("group")
            overrides = config.get("overrides")

            _sim_start_time = datetime.now()

            # Execute simulation
            success = run_simulation(
                alg=alg,
                runs=runs,
                config_index=LIST_OF_CONFIGS.index(config) + 1,
                bp=bp,
                run_id=id,
                group=group,
                overrides_list=overrides,
                verify=args.verify,
                do_continue=args.do_continue,
                parent_dir_id=args.parent_dir_id,
                custom_cfg=args.runcfg,
                alg_override=args.algorithm,
                report_base=args.setreportspath or REPORTS_BASE,
                continue_on_error=args.continue_on_error
            )

            _sim_end_time = datetime.now()
            running_times.append(_sim_end_time - _sim_start_time)

            if success:
                successes += 1
            else:
                failures += 1
    else:
        config_num = args.config

        if not config_num:
            log.error("No config specified. Use -c or --config to specify a config index.")
            sys.exit(1)

        # Parse config indices supporting ranges with hyphens
        configs_to_run: list[int] = parse_config_indices(config_num)

        log.info("Running %s configurations.", len(configs_to_run))
        for config_num in configs_to_run:
            # Validate whether config num is in range
            if config_num < 1 or config_num > len(LIST_OF_CONFIGS):
                log.warning(
                    "Config index %s out of range [1, %s]",
                    config_num,
                    len(LIST_OF_CONFIGS),
                )
                continue

            config = LIST_OF_CONFIGS[config_num - 1]
            alg = config["alg"]

            runs = check_runs(args.runs, config)

            bp = config["bp"] if "bp" in config else None
            id = config["id"]
            group = config.get("group")
            overrides = config.get("overrides")

            _sim_start_time = datetime.now()

            # Execute simulation
            success = run_simulation(
                alg=alg,
                runs=runs,
                config_index=config_num,
                bp=bp,
                run_id=id,
                group=group,
                overrides_list=overrides,
                verify=args.verify,
                do_continue=args.do_continue,
                parent_dir_id=args.parent_dir_id,
                custom_cfg=args.runcfg,
                alg_override=args.algorithm,
                report_base=args.setreportspath or REPORTS_BASE,
                continue_on_error=args.continue_on_error
            )


            _sim_end_time = datetime.now()

            if success:
                successes += 1
            else:
                failures += 1

    end_time = datetime.now()
    sum_running_time = sum(running_times, timedelta())
    avg_running_time = (sum_running_time // len(running_times)) if len(running_times) > 1 else sum_running_time

    log.info("%s", "=" * LINE_LENGTH)
    log.info(
        "[SUMMARY] Batch run completed at %s, time taken: %s, average running time: %s",
        end_time,
        format_timedelta(end_time - start_time),
        format_timedelta(avg_running_time),
    )
    log.info(
        "[SUMMARY] Total configurations run: %s (Success: %s, Failed: %s) - Errors count as Failed",
        successes + failures,
        successes,
        failures,
    )
    log.info("%s", "=" * LINE_LENGTH)

    if (args.verify or args.do_continue) and failures > 0:
        sys.exit(1)
