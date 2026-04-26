"""
The second version of batch runner, will provide better and more flexible runs.
"""

# ------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------------------------------------------- #

import os
import sys
import argparse
import subprocess
import datetime as dt
import json
from typing import Optional, Tuple

from datetime import datetime, timedelta

from pyrunner.utils.fs import safe_int_dirnames
from pyrunner.utils.jsonio import load_json_file
from pyrunner.utils.path import validate_run_id
from pyrunner.utils.timefmt import format_timedelta

LINE_LENGTH = 100


# ------------------------------------------------------------------------------------------------------------------- #
# BATCH RUNNER CONFIGURATION
# ------------------------------------------------------------------------------------------------------------------- #


ID_LABEL = "ID_LABEL"
ALG_LABEL = "ALG_LABEL"

alg_base_settings = {
    "ql": "settings/skripsi/randomsearch-qlearn.cfg",
    "mc": "settings/skripsi/randomsearch-mc.cfg",
    "lfe": "settings/skripsi/randomsearch-lf-episodic.cfg",
}

alg_abbreviations = {
    "ql": "QLearningMovement",
    "mc": "MCMovement",
    "lfe": "LevyFlightEpisodic",
}

behavior_packages = {
    "epsilon": "movement.rl.behavior.EpsilonGreedyBehavior",
    "ucb": "movement.rl.behavior.UCBBehavior",
    "ts": "movement.rl.behavior.ThompsonSamplingBehavior"
}

key_abbreviations = {
    # [ Agent movement settings ]
    "amm": "Group1.movementModel",
    "tmm": "Group2.movementModel",

    # [ Report settings ]
    "r_dir": "Report.reportDir",

    # [ QLearningMovement settings ]
    "qlm_bp": "QLearningMovement.behaviorPolicy",
    "qlm_lr": "QLearningMovement.learningRate",
    "qlm_df": "QLearningMovement.discountFactor",
    "qlm_iq": "QLearningMovement.initialQValue",
    "qlm_tp": "QLearningMovement.targetPrefix",
    "qlm_sp": "QLearningMovement.stepPenalty",
    "qlm_fr": "QLearningMovement.foundReward",
    "qlm_as": "QLearningMovement.agentSpeed",

    # [ Monte-Carlo Movement settings ]
    "mcm_bp": "MCMovement.behaviorPolicy",
    "mcm_lr": "MCMovement.learningRate",
    "mcm_df": "MCMovement.discountFactor",
    "mcm_iq": "MCMovement.initialQValue",
    "mcm_tp": "MCMovement.targetPrefix",
    "mcm_sp": "MCMovement.stepPenalty",
    "mcm_fr": "MCMovement.foundReward",
    "mcm_as": "MCMovement.agentSpeed",
    "mcm_fv": "MCMovement.firstVisit",

    # [ Lévy Flight Episodic Movement settings ]
    "lfe_la": "LevyFlightEpisodic.levyAlpha",
    "lfe_xm": "LevyFlightEpisodic.xm",
    "lfe_tp": "LevyFlightEpisodic.targetPrefix",
    "lfe_fs": "LevyFlightEpisodic.flightSpeed",
    "lfe_sp": "LevyFlightEpisodic.stepPenalty",
    "lfe_fr": "LevyFlightEpisodic.foundReward",

    # [ EpsilonGreedyBehavior settings ]
    "eg_ip": "BehaviorPolicy.epsilon",
    "eg_ed": "BehaviorPolicy.epsilonDecay",
    "eg_me": "BehaviorPolicy.minEpsilon",

    # [ UCBBehavior settings ]
    "ucb_ec": "BehaviorPolicy.UCB.explorationConstant",

    # [ TSBehavior settings ]
    "ts_iv": "BehaviorPolicy.TS.initialVariance",

    # [ EpisodicPersistenceManager settings ]
    "epm_ep": "EpisodicPersistenceManager.episodeNumber",
    "epm_path": "EpisodicPersistenceManager.persistencePath",
    "epm_saves": "EpisodicPersistenceManager.saveEpisodically",

    # [ Movement model settings ]
    "m_seed": "MovementModel.seed",
    "m_ws": "MovementModel.worldSize",

}

S_REPORT_DIR = f"Report.reportDir=reports/skripsi/{ALG_LABEL}/run-id/{ID_LABEL}"

PRIORITY_OVERRIDE_KEYS = ["lfe_la", "qlm_bp", "mcm_bp"]

# Import the configs
from pyrunner.batch_configs import LIST_OF_CONFIGS


def create_config_setting_json(
        alg: str,
        parent_dir_id: str,
        runs: int,
        bp: Optional[str],
        result_dir_id: str = None,
        overrides_list: list[str] = None
):
    config_setting_json = {
        "runner_episodes:" : runs,
        "runner_id": result_dir_id,

        "alg": alg,
        "parent_dir_id": parent_dir_id,

        "amm": alg_abbreviations[alg],
    }

    bp_key = _get_bp_override_key(alg)
    if bp and bp_key:
        config_setting_json[bp_key] = behavior_packages[bp]

    for entry in overrides_list or []:
        key, value = entry.split("=", 1)
        config_setting_json[key] = value

    # Create the direcetory first
    dir_path = f"reports/skripsi/{parent_dir_id}/run-id/{result_dir_id}"
    os.makedirs(dir_path, exist_ok=True)

    # Save the JSON to the report directory
    with open(f"reports/skripsi/{parent_dir_id}/run-id/{result_dir_id}/config_setting.json", "w") as json_file:
        json.dump(config_setting_json, json_file, indent=4)


def parse_overrides(overrides_dict: dict[str]) -> Tuple[list[str], list[str]]:
    # convert the override dictionary into a list of key-value
    abr_overrides_list = []
    full_overrides_list = []
    for key, value in overrides_dict.items():

        # Check if key is an abbreviation
        if key in key_abbreviations:
            full_key = key_abbreviations[key]
        else:
            # Use the key as-is (assuming the real setting full key)
            full_key = key

        abr_overrides_list.append(f"{key}@{value}")
        full_overrides_list.append(f"{full_key}={value}")

    return abr_overrides_list, full_overrides_list


def _get_bp_override_key(alg: str) -> Optional[str]:
    if alg == "ql":
        return "qlm_bp"
    if alg == "mc":
        return "mcm_bp"
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


def expand_algorithm(alg: str) -> str:
    if alg not in alg_base_settings:
        raise ValueError(
            f"Unknown algorithm '{alg}'. Valid options: {', '.join(alg_base_settings.keys())}"
        )
    return alg_base_settings[alg]


def build_result_id_dir(
        alg: str,
        runs: int,
        config_index: int,
        overrides: list[str],
        run_id: Optional[str]
) -> str:
    prefix = f"cfg@{config_index}-{alg}{runs}"
    ordered_overrides = _order_abbreviated_overrides(overrides)

    if ordered_overrides:
        suffix = "-".join(ordered_overrides)
    else:
        suffix = run_id or ""

    return f"{prefix}-{suffix}" if suffix else prefix


def run_script(algo: str, overrides_string: str = None, ep: int = -1) -> bool:
    script = [
        r".\one.bat",
        "-b",
        "1",
    ]

    # Add overrides only if provided
    if overrides_string:
        script.extend(["-d", overrides_string])

    # Add config file path
    script.append(alg_base_settings[algo])

    _start_time = None

    try:
        _start_time = datetime.now()

        print(f"{'-' * LINE_LENGTH}")
        print(f"[{_start_time.strftime("%H:%M:%S")}] Running episode {str(ep)} for algorithm {algo}.")
        print(f"{'-' * LINE_LENGTH}\n")

        print(f"[{_start_time.strftime("%H:%M:%S")}] Running command: {' '.join(script)}")
        subprocess.run(script, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        _end_time = datetime.now()

        print(f"[{_end_time.strftime("%H:%M:%S")}] Error running episode {ep} for algorithm {algo}.")
        return False
    finally:
        _end_time = datetime.now()

        print(f"{'-' * LINE_LENGTH}")
        print(f"[{_end_time.strftime("%H:%M:%S")}] Done running episode {str(ep)} for algorithm {algo}. Took {format_timedelta(_end_time - _start_time)}.")
        print(f"{'-' * LINE_LENGTH}\n")


def find_highest_good_episode(full_report_dir: str) -> Tuple[int, list[str], bool]:
    """Determine highest *contiguous* episode number (starting from 1) in which Persistence-Episode@N.json is readable JSON.

    Returns: (highest_good, problems, episodic_available)
    - highest_good is 0 if none are valid.
    - episodic_available False means ep/ directory missing (saveEpisodically likely false).
    """
    problems: list[str] = []
    ep_root = os.path.join(full_report_dir, "ep")
    if not os.path.isdir(ep_root):
        return 0, [f"[WARN] Episodic directory not found: {ep_root} (saveEpisodically likely false)"] , False

    episode_dirs = safe_int_dirnames(ep_root)
    if not episode_dirs:
        problems.append(f"[WARN] No episode directories found under: {ep_root}")
        return 0, problems, True

    highest_good = 0
    # Contiguous check from 1... until first failure
    for expected in range(1, max(episode_dirs) + 1):
        if expected not in episode_dirs:
            problems.append(f"[FAIL] Missing episode directory: {os.path.join(ep_root, str(expected))}")
            break

        persistence_path = os.path.join(ep_root, str(expected), f"Persistence-Episode@{expected}.json")
        ok, data, err = load_json_file(persistence_path)
        if not ok:
            problems.append(f"[FAIL] Episode {expected} persistence unreadable: {persistence_path} ({err})")
            break

        # If episodeNumber exists, ensure the stored Persistence JSON data matches
        if "episodeNumber" in data:
            try:
                if int(data["episodeNumber"]) != expected:
                    problems.append(
                        f"[FAIL] Episode {expected} persistence mismatch: episodeNumber={data['episodeNumber']} in {persistence_path}"
                    )
                    break
            except (TypeError, ValueError):
                problems.append(f"[FAIL] Episode {expected} persistence has non-integer episodeNumber in {persistence_path}")
                break

        highest_good = expected

    return highest_good, problems, True


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
        overrides_list: Optional[dict[str]] = None,
        verify: bool = False,
        do_continue: bool = False,
        parent_dir_id: Optional[str] = None
) -> bool:
    # Validate algorithm
    settings_file = expand_algorithm(alg)

    # Validate behavior policy if provided
    if bp and bp not in behavior_packages:
        raise ValueError(
            f"Unknown behavior policy '{bp}'. Valid options: {', '.join(behavior_packages.keys())}"
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
            full_overrides.append(f"{key_abbreviations[bp_override_key]}={behavior_packages[bp]}")

    result_id_dir = build_result_id_dir(alg, runs, config_index, abr_overrides, run_id)
    validate_run_id(result_id_dir)

    # Allow overriding the {alg} portion of reports/skripsi/{alg}/run-id/{result_id_dir}
    parent_dir_id_effective = (parent_dir_id or alg).strip()
    validate_run_id(parent_dir_id_effective)
    full_report_dir = f"reports/skripsi/{parent_dir_id_effective}/run-id/{result_id_dir}"

    persistence_override = f"EpisodicPersistenceManager.persistencePath={full_report_dir}/_persistence.json"
    full_overrides.append(persistence_override)

    overrides_string = "@@".join(full_overrides) if full_overrides else None

    # Print run information
    print(f"\n{'=' * LINE_LENGTH}")
    print(f"[INFO] Starting episodic simulation batch...")
    print(f"[INFO] Algorithm: {alg} ({settings_file}), Behavior Policy: {bp}")
    print(f"[INFO] Run ID: {run_id}, Number of episodes: {runs}")
    print(f"[INFO] Report parent dir id: {parent_dir_id_effective} (reports/skripsi/{parent_dir_id_effective}/...)")
    print(f"[INFO] Overrides: {overrides_string if overrides_string else 'None'}")
    print(f"{'=' * LINE_LENGTH}\n")

    # Create a JSON to log the current running simulation configuration
    create_config_setting_json(alg, parent_dir_id_effective, runs, bp, result_id_dir, full_overrides)

    # Verification / continue pre-flight
    start_ep = 1
    highest_good = 0
    episodic_available = True
    if verify or do_continue:
        highest_good, problems, episodic_available = find_highest_good_episode(full_report_dir)
        expected_last = runs

        print(f"\n{'-' * LINE_LENGTH}")
        print(f"[INFO] [VERIFY] Run dir: {full_report_dir}")
        print(f"[INFO] [VERIFY] Expected episodes (runs): {expected_last}")
        print(f"[INFO] [VERIFY] Highest contiguous uncorrupted episode: {highest_good}")
        if problems:
            for p in problems:
                print(p)
        if episodic_available:
            if highest_good >= expected_last:
                print(f"[INFO] [VERIFY] ✅ Complete ({highest_good}/{expected_last})")
            else:
                print(f"[INFO] [VERIFY] ❌ Incomplete ({highest_good}/{expected_last})")
        else:
            print("[INFO] [VERIFY] [WARN] Cannot verify episodic persistence (saveEpisodically likely false).")
        print(f"{'-' * LINE_LENGTH}\n")

        if not episodic_available:
            print("[INFO] [VERIFY] [WARN] Episodic snapshots missing. Exiting with error code 1.")
            return False

        if do_continue:
            if not episodic_available:
                # Per requirement: restart from 0 (effectively episode 1), but print warning and highest uncorrupted episode.
                print("[INFO] [CONTINUE] Episodic snapshots not available; cannot rebuild from ep/N. Will restart from episode 1.")
                start_ep = 1
            elif highest_good <= 0:
                print("[INFO] [CONTINUE] No readable episodic snapshot found; will restart from episode 1.")
                start_ep = 1
            else:
                # Rebuild main persistence from last good, then resume from the next episode.
                # Assumption: if Persistence-Episode@K.json exists and is readable, K is uncorrupted.
                ok, msg = rebuild_main_persistence_from_episode(full_report_dir, highest_good)
                if ok:
                    print(f"[INFO] [CONTINUE] {msg}")
                else:
                    print(f"[INFO] [CONTINUE] [WARN] {msg}")

                start_ep = highest_good + 1
                if start_ep > runs:
                    print(f"[INFO] [CONTINUE] Already complete ({highest_good}/{runs}). Nothing to continue.")
                    return True

            if highest_good > 0 and start_ep <= runs:
                print(f"[INFO] [CONTINUE] Highest uncorrupted episode: {highest_good}. Resuming from episode {start_ep} (next episode).")

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
        if run_script(alg, running_overrides_string, ep):
            succeeds += 1
        else:
            failed += 1

    end_time = datetime.now()

    # Print summary
    print(f"\n{'=' * LINE_LENGTH}")
    print(f"[INFO] Episodic simulation batch completed at {end_time}, time taken: {format_timedelta(end_time - start_time)}")
    print(f"[INFO] Total episodes: {runs} (Success: {succeeds}, Fails: {failed})")
    print(f"{'=' * LINE_LENGTH}\n")

    return failed == 0


def check_runs(args_runs: int, config: dict[str, str] = None) -> int:
    _runs = 0
    if args_runs:
        if args_runs <= 0:
            print(f"Invalid number of runs: {args_runs}")
            sys.exit(1)
        _runs = args_runs
    else:
        if not config["runs"]:
            print(f"No number of runs specified in config: {config['id']}")
            sys.exit(1)
        if config["runs"] and config["runs"] <= 0:
            print(f"Invalid number of runs in config: {config['runs']}")
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
        "-r", "--runs", type=int, help="Number of runs for the simulation (overrides the existing configs)", required=False
    )

    parser.add_argument(
        "-cc", "--count-configs", action="store_true", help="Count the number of configs in the LIST_OF_CONFIGS and exit"
    )

    parser.add_argument(
        "-pid", "--parent-dir-id", type=str, required=False,
        help="Override script report dir base folder name under reports/skripsi/. Default uses algorithm key (e.g., 'ql')."
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

    # Parse arguments
    args = parser.parse_args()

    # -vc is equivalent to --verify --continue
    if getattr(args, "vc", False):
        args.verify = True
        args.do_continue = True

    if args.count_configs:
        print(f"Number of configs: {len(LIST_OF_CONFIGS)}")
        sys.exit(0)

    successes = 0
    failures = 0

    start_time = datetime.now()
    running_times = []

    if args.all:
        print(f"[INFO] Running {len(LIST_OF_CONFIGS)} configurations.")
        for config in LIST_OF_CONFIGS:
            alg = config["alg"]

            runs = check_runs(args.runs, config)

            bp = config["bp"]
            id = config["id"]
            overrides = config.get("overrides")

            _sim_start_time = datetime.now()

            # Execute simulation
            success = run_simulation(
                alg=alg,
                runs=runs,
                config_index=LIST_OF_CONFIGS.index(config) + 1,
                bp=bp,
                run_id=id,
                overrides_list=overrides,
                verify=args.verify,
                do_continue=args.do_continue,
                parent_dir_id=args.parent_dir_id
            )

            _sim_end_time = datetime.now()
            running_times.append(_sim_end_time - _sim_start_time)

            if success:
                successes += 1
            else:
                failures += 1
    else:
        config_num = args.config

        # Parse config indices supporting ranges with hyphens
        configs_to_run: list[int] = parse_config_indices(config_num)

        print(f"[INFO] Running {len(configs_to_run)} configurations.")
        for config_num in configs_to_run:
            # Validate whether config num is in range
            if config_num < 1 or config_num > len(LIST_OF_CONFIGS):
                print(f"Config index {config_num} out of range [1, {len(LIST_OF_CONFIGS)}]")
                continue

            config = LIST_OF_CONFIGS[config_num - 1]
            alg = config["alg"]

            runs = check_runs(args.runs, config)

            bp = config["bp"]
            id = config["id"]
            overrides = config.get("overrides")

            _sim_start_time = datetime.now()

            # Execute simulation
            success = run_simulation(
                alg=alg,
                runs=runs,
                config_index=config_num,
                bp=bp,
                run_id=id,
                overrides_list=overrides,
                verify=args.verify,
                do_continue=args.do_continue,
                parent_dir_id=args.parent_dir_id
            )

            _sim_end_time = datetime.now()
            running_times.append(_sim_end_time - _sim_start_time)

            if success:
                successes += 1
            else:
                failures += 1

    end_time = datetime.now()
    sum_running_time = sum(running_times, timedelta())
    avg_running_time = sum_running_time // len(running_times)

    print(f"\n{'=' * LINE_LENGTH}")
    print(f"[SUMMARY] Batch run completed at {end_time}, time taken: {format_timedelta(end_time - start_time)}, average running time: {format_timedelta(avg_running_time)}")
    print(f"[SUMMARY] Total configurations run: {successes + failures} (Success: {successes}, Failed: {failures})")

    print(f"{'=' * LINE_LENGTH}\n")

    if (args.verify or args.do_continue) and failures > 0:
        sys.exit(1)

