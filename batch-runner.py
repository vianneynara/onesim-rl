"""
The second version of batch runner, will provide better and more flexible runs.
"""

# ------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------------------------------------------- #

import re
import sys
import argparse
import subprocess
import datetime as dt

from datetime import datetime

# ------------------------------------------------------------------------------------------------------------------- #
# PATH VALIDATOR
# ------------------------------------------------------------------------------------------------------------------- #

# Characters not allowed in Windows filenames/path components
INVALID_CHARS_RE = re.compile(r'[<>:"/\\|?*]')
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}


def validate_run_id(run_id: str) -> None:
    """
    Static method to validate the run_id safety to use as a Windows path component.

    Raises ValueError with a clear message if invalid.
    """
    if not run_id:
        raise ValueError("run_id must not be empty")

    # Check for illegal characters
    if INVALID_CHARS_RE.search(run_id):
        raise ValueError(
            f"run_id '{run_id}' contains invalid path characters. "
            r"Disallowed characters are: < > : \" / \ | ? *"
        )

    # Check for control chars (ASCII 0-31)
    if any(ord(ch) < 32 for ch in run_id):
        raise ValueError(
            f"run_id '{run_id}' contains control characters, which are not "
            "allowed in Windows filenames."
        )

    # Check for reserved device names (case-insensitive, exact matches only)
    if run_id.upper() in WINDOWS_RESERVED_NAMES:
        raise ValueError(
            f"run_id '{run_id}' is a reserved device name on Windows "
            "(CON, PRN, AUX, NUL, COM1..COM9, LPT1..LPT9). "
            "Please choose a different run_id."
        )


def format_timedelta(td):
    # Calculate total components
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"


# ------------------------------------------------------------------------------------------------------------------- #
# BATCH RUNNER CONFIGURATION
# ------------------------------------------------------------------------------------------------------------------- #


ID_LABEL = "ID_LABEL"
ALG_LABEL = "ALG_LABEL"

alg_base_settings = {
    "ql": "settings/skripsi/randomsearch-qlearn.cfg",
    "lfe": "settings/skripsi/randomsearch-lf-episodic.cfg",
    "lf": "settings/skripsi/randomsearch-lf.cfg"
}

behavior_packages = {
    "epsilon": "movement.rl.behavior.EpsilonGreedyBehavior",
    "ucb": "movement.rl.behavior.UCBBehavior",
    "ts": "movement.rl.behavior.ThompsonSamplingBehavior"
}

key_abbreviations = {
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
    "epm_saves": "EpisodicPersistenceManager.saveEpisodically"
}

S_REPORT_DIR = f"Report.reportDir=reports/skripsi/{ALG_LABEL}/run-id/{ID_LABEL}"

LIST_OF_CONFIGS = [
    {
        "alg": "ql",
        "runs": 5,
        "bp": "epsilon",
        "id": "ql5-bp=epsilon",
        "overrides": {
            "eg_ip": 1.0,
            "eg_ed": 0.999999,
            "eg_me": 0.1,
        }
    },
    {
        "alg": "ql",
        "runs": 5,
        "bp": "ucb",
        "id": "ql5-bp=ucb",
        "overrides": {
            "ucb_ec": 2.0,
        }
    },
    {
        "alg": "ql",
        "runs": 5,
        "bp": "ts",
        "id": "ql5-bp=ts",
        "overrides": {
            "ts_iv": 1.0,
        }
    }
]


def parse_overrides(overrides_dict: dict[str]) -> str:
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


def expand_algorithm(alg: str) -> str:
    if alg not in alg_base_settings:
        raise ValueError(
            f"Unknown algorithm '{alg}'. Valid options: {', '.join(alg_base_settings.keys())}"
        )
    return alg_base_settings[alg]


def build_result_id_dir(alg: str, runs: int, bp: str = None, overrides: list[str] = None) -> str:
    # Initial first part  of algorithm and runs
    result_id_dir = f"{alg}{runs}-qlm_bp@{bp}-"

    # Adds overrides if exist
    result_id_dir += "-".join(overrides) if overrides else ""

    return result_id_dir


def run_script(algo: str, overrides_string: str = None, ep: int = -1) -> bool:
    _current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"[{_current_time}] Running episode {str(ep)} for algorithm {algo}.")
    print(f"[{_current_time}] ============================================================")

    script = [
        r".\one.bat",
        "-b", "1",
    ]

    # Add overrides only if provided
    if overrides_string:
        script.extend(["-d", overrides_string])

    # Add config file path
    script.append(alg_base_settings[algo])

    try:
        print(f"[{_current_time}] Running command: {' '.join(script)}")
        subprocess.run(script, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        print(f"[{_current_time}] Error running episode {ep} for algorithm {algo}.")
        return False


def run_simulation(alg: str, runs: int, bp: str, run_id: str = None, overrides_list: list[str] = None) -> bool:
    # Validate algorithm
    settings_file = expand_algorithm(alg)

    # Validate behavior policy
    if bp not in behavior_packages:
        raise ValueError(
            f"Unknown behavior policy '{bp}'. Valid options: {', '.join(behavior_packages.keys())}"
        )

    abr_overrides, full_overrides = [], []

    # Build the base overrides
    if overrides_list:
        abr_overrides, full_overrides  = parse_overrides(overrides_list)

    result_id_dir = build_result_id_dir(alg, runs, bp, abr_overrides)
    validate_run_id(result_id_dir)
    full_report_dir = f"reports/skripsi/{alg}/run-id/{result_id_dir}"

    bp_override = f"QLearningMovement.behaviorPolicy={behavior_packages[bp]}"
    persistence_override = f"EpisodicPersistenceManager.persistencePath={full_report_dir}/_persistence.json"

    if overrides_list and full_overrides:
        full_overrides.append(bp_override)
        full_overrides.append(persistence_override)

    overrides_string = "@@".join(full_overrides)

    # Print run information
    print(f"\n{'=' * 70}")
    print(f"[INFO] Starting episodic simulation batch...")
    print(f"[INFO] Algorithm: {alg} ({settings_file}), Behavior Policy: {bp}")
    print(f"[INFO] Run ID: {run_id}, Number of episodes: {runs}")
    print(f"[INFO] Overrides: {overrides_string if overrides_string else 'None'}")
    print(f"{'=' * 70}\n")

    # Execute episodes
    succeeds = 0
    failed = 0
    start_time = datetime.now()

    for ep in range(1, runs + 1):
        running_overrides_string = (
                overrides_string
                + f"@@Report.reportDir={full_report_dir}/ep/{str(ep)}"
                + f"@@EpisodicPersistenceManager.episodeNumber={str(ep)}"
        )
        if run_script(alg, running_overrides_string, ep):
            succeeds += 1
        else:
            failed += 1

    end_time = datetime.now()

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"[INFO] Episodic simulation batch completed at {end_time}, time taken: {format_timedelta(end_time-start_time)}")
    print(f"[INFO] Total episodes: {runs} (Success: {succeeds}, Fails: {failed})")
    print(f"{'=' * 70}\n")

    return failed == 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="ONE Simulator multi-run/episodic launcher (version 2), simpler"
    )
    parser.add_argument(
        "-c", "--config", type=int, help="Config index to run", required=False
    )

    parser.add_argument(
        "-a", "--all", action="store_true", help="Run all configs"
    )

    # Parse arguments
    args = parser.parse_args()

    success = False
    if args.all:
        successes = 0
        failures = 0

        for config in LIST_OF_CONFIGS:
            alg = config["alg"]
            runs = config["runs"]
            bp = config["bp"]
            id = config["id"]
            overrides = config["overrides"] if "overrides" in config else args.d

            # Execute simulation
            success = run_simulation(
                alg=alg,
                runs=runs,
                bp=bp,
                run_id=id,
                overrides_list=overrides
            )
    else:
        config_idx = args.config
        if config_idx < 0 or config_idx >= len(LIST_OF_CONFIGS):
            raise ValueError(
                f"Config index {config_idx} out of range [0, {len(LIST_OF_CONFIGS) - 1}]"
            )
        config = LIST_OF_CONFIGS[config_idx]
        alg = config["alg"]
        runs = config["runs"]
        bp = config["bp"]
        id = config["id"]
        overrides = config["overrides"] if "overrides" in config else args.d

        # Execute simulation
        success = run_simulation(
            alg=alg,
            runs=runs,
            bp=bp,
            run_id=id,
            overrides_list=overrides
        )

    sys.exit(0 if success else 1)
