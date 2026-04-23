"""
The second version of batch runner, will provide better and more flexible runs.
"""

# ------------------------------------------------------------------------------------------------------------------- #
# IMPORTS
# ------------------------------------------------------------------------------------------------------------------- #

import os
import re
import sys
import argparse
import subprocess
import datetime as dt
import json

from datetime import datetime, timedelta

# ------------------------------------------------------------------------------------------------------------------- #
# TELEGRAM NOTIFIER
# ------------------------------------------------------------------------------------------------------------------- #

def load_telegram_config(config_path: str = "telegram_config.json") -> dict:
    """
    Loads Telegram bot token and chat ID from a JSON file.

    Expected format of telegram_config.json:
    {
        "bot_token": "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ",
        "chat_id": "987654321"
    }
    """
    if not os.path.exists(config_path):
        print(f"[TELEGRAM] Config file '{config_path}' not found. Telegram notifications disabled.")
        return None
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
        if "bot_token" not in cfg or "chat_id" not in cfg:
            print("[TELEGRAM] Config missing 'bot_token' or 'chat_id'. Telegram notifications disabled.")
            return None
        return cfg
    except Exception as e:
        print(f"[TELEGRAM] Failed to load config: {e}. Telegram notifications disabled.")
        return None


def send_telegram(cfg: dict, message: str) -> bool:
    """
    Sends a message to a Telegram chat using the Bot API.
    Returns True on success, False on failure.
    Does NOT raise — notification failure must never crash the simulation.
    """
    if cfg is None:
        return False
    try:
        import urllib.request
        url = f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage"
        payload = json.dumps({
            "chat_id": cfg["chat_id"],
            "text": message,
            "parse_mode": "HTML"
        }).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"[TELEGRAM] Failed to send message: {e}")
        return False


# ------------------------------------------------------------------------------------------------------------------- #
# PC BEEP NOTIFICATION
# ------------------------------------------------------------------------------------------------------------------- #

def beep_done():
    """
    Plays a beep/notification sound on Windows, macOS, or Linux.
    Silent fail if the platform does not support it.
    """
    try:
        if sys.platform == "win32":
            import winsound
            # Three short beeps to signal completion
            for _ in range(3):
                winsound.Beep(1000, 300)
                import time; time.sleep(0.1)
        elif sys.platform == "darwin":
            # macOS system bell
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], check=False)
        else:
            # Linux — try paplay, then fallback to terminal bell
            result = subprocess.run(["paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"],
                                    check=False, capture_output=True)
            if result.returncode != 0:
                print("\a", end="", flush=True)  # terminal bell fallback
    except Exception as e:
        print(f"[BEEP] Could not play sound: {e}")


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
    "mc": "settings/skripsi/randomsearch-mc.cfg",
    "mcn": "settings/skripsi/randomsearch-mcn.cfg",
    "lfe": "settings/skripsi/randomsearch-lf-episodic.cfg",
    "lf": "settings/skripsi/randomsearch-lf.cfg"
}

alg_abbreviations = {
    "ql": "QLearningMovement",
    "mc": "MCMovement",
    "mcn": "MCMovementEnd",
    "lfe": "LevyFlightEpisodic",
    "lf": "LevyFlight"
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

    # [ MCMovement settings ]
    "mcm_bp": "MCMovement.behaviorPolicy",
    "mcm_lr": "MCMovement.learningRate",
    "mcm_df": "MCMovement.discountFactor",
    "mcm_iq": "MCMovement.initialQValue",
    "mcm_tp": "MCMovement.targetPrefix",
    "mcm_sp": "MCMovement.stepPenalty",
    "mcm_fr": "MCMovement.foundReward",
    "mcm_as": "MCMovement.agentSpeed",
    "mcm_fv": "MCMovement.firstVisit",

    # [ MCMovementEnd settings ]
    "mcmn_bp": "MCMovementEnd.behaviorPolicy",
    "mcmn_lr": "MCMovementEnd.learningRate",
    "mcmn_df": "MCMovementEnd.discountFactor",
    "mcmn_iq": "MCMovementEnd.initialQValue",
    "mcmn_tp": "MCMovementEnd.targetPrefix",
    "mcmn_sp": "MCMovementEnd.stepPenalty",
    "mcmn_fr": "MCMovementEnd.foundReward",
    "mcmn_as": "MCMovementEnd.agentSpeed",
    "mcmn_fv": "MCMovementEnd.firstVisit",

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

# Import the configs
from batch_configs import LIST_OF_CONFIGS

def create_config_setting_json(alg: str, runs: int, bp: str, result_dir_id: str = None, overrides_list: list[str] = None):
    config_setting_json = {
        "runner_episodes:" : runs,
        "runner_id": result_dir_id,

        "amm": alg_abbreviations[alg],

        # dont know what
        "mcmn_bp": behavior_packages[bp],
    }

    for entry in overrides_list:
        key, value = entry.split("=")
        config_setting_json[key] = value

    # Create the direcetory first
    dir_path = f"reports/skripsi/{alg}/run-id/{result_dir_id}"
    os.makedirs(dir_path, exist_ok=True)

    # Save the JSON to the report directory
    with open(f"reports/skripsi/{alg}/run-id/{result_dir_id}/config_setting.json", "w") as json_file:
        json.dump(config_setting_json, json_file, indent=4)


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


def run_script(algo: str, overrides_string: str = None, ep: int = -1, tg_cfg: dict = None) -> bool:
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

        print(f"{'-' * 70}")
        print(f"[{_start_time.strftime('%H:%M:%S')}] Running episode {str(ep)} for algorithm {algo}.")
        print(f"{'-' * 70}\n")

#         # Telegram: notify episode start
#         send_telegram(tg_cfg,
#             f"▶️ <b>Episode {ep} started</b>\n"
#             f"Algorithm: <code>{algo}</code>\n"
#             f"Time: {_start_time.strftime('%H:%M:%S')}"
#         )

        print(f"[{_start_time.strftime('%H:%M:%S')}] Running command: {' '.join(script)}")
        subprocess.run(script, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        _end_time = datetime.now()

        print(f"[{_end_time.strftime('%H:%M:%S')}] Error running episode {ep} for algorithm {algo}.")

#         # Telegram: notify episode failure
#         send_telegram(tg_cfg,
#             f"❌ <b>Episode {ep} FAILED</b>\n"
#             f"Algorithm: <code>{algo}</code>\n"
#             f"Time: {_end_time.strftime('%H:%M:%S')}"
#         )
        return False
    finally:
        _end_time = datetime.now()
        elapsed = format_timedelta(_end_time - _start_time)

        print(f"{'-' * 70}")
        print(f"[{_end_time.strftime('%H:%M:%S')}] Done running episode {str(ep)} for algorithm {algo}. Took {elapsed}.")
        print(f"{'-' * 70}\n")

        # Telegram: notify episode done (success path — failure already sent above)


def run_simulation(alg: str, runs: int, bp: str, run_id: str = None, overrides_list: list[str] = None, tg_cfg: dict = None) -> bool:
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
        abr_overrides, full_overrides = parse_overrides(overrides_list)

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

    # Telegram: notify config start
    send_telegram(tg_cfg,
        f"🚀 <b>Config started</b>\n"
        f"Algorithm: <code>{alg}</code> | Policy: <code>{bp}</code>\n"
        f"Run ID: <code>{result_id_dir}</code>\n"
        f"Episodes: {runs}\n"
        f"Time: {datetime.now().strftime('%H:%M:%S')}"
    )

    # Create a JSON to log the current running simulation configuration
    create_config_setting_json(alg, runs, bp, result_id_dir, full_overrides)

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
        if run_script(alg, running_overrides_string, ep, tg_cfg):
            succeeds += 1

#             # Telegram: episode success
#             send_telegram(tg_cfg,
#                 f"✅ <b>Episode {ep}/{runs} done</b>\n"
#                 f"Algorithm: <code>{alg}</code>\n"
#                 f"Success so far: {succeeds} | Failed: {failed}"
#             )
        else:
            failed += 1

    end_time = datetime.now()
    elapsed = format_timedelta(end_time - start_time)

    # Print summary
    print(f"\n{'=' * 70}")
    print(f"[INFO] Episodic simulation batch completed at {end_time}, time taken: {elapsed}")
    print(f"[INFO] Total episodes: {runs} (Success: {succeeds}, Fails: {failed})")
    print(f"{'=' * 70}\n")

    # Telegram: notify config done
    send_telegram(tg_cfg,
        f"{'✅' if failed == 0 else '⚠️'} <b>Config finished</b>\n"
        f"Algorithm: <code>{alg}</code> | Policy: <code>{bp}</code>\n"
        f"Run ID: <code>{result_id_dir}</code>\n"
        f"Episodes: {runs} (✅ {succeeds} / ❌ {failed})\n"
        f"Time taken: {elapsed}"
    )

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

    # Parse arguments
    args = parser.parse_args()

    if args.count_configs:
        print(f"Number of configs: {len(LIST_OF_CONFIGS)}")
        sys.exit(0)

    # Load Telegram config once at startup
    tg_cfg = load_telegram_config("telegram_config.json")
    if tg_cfg:
        print("[TELEGRAM] Notifications enabled.")
        send_telegram(tg_cfg,
            f"🤖 <b>Batch runner started</b>\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
    else:
        print("[TELEGRAM] Notifications disabled.")

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
            overrides = config["overrides"] if "overrides" in config else args.d

            _sim_start_time = datetime.now()

            # Execute simulation
            success = run_simulation(
                alg=alg,
                runs=runs,
                bp=bp,
                run_id=id,
                overrides_list=overrides,
                tg_cfg=tg_cfg
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
            overrides = config["overrides"] if "overrides" in config else args.d

            _sim_start_time = datetime.now()

            # Execute simulation
            success = run_simulation(
                alg=alg,
                runs=runs,
                bp=bp,
                run_id=id,
                overrides_list=overrides,
                tg_cfg=tg_cfg
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
    total_elapsed = format_timedelta(end_time - start_time)

    print(f"\n{'=' * 70}")
    print(f"[SUMMARY] Batch run completed at {end_time}, time taken: {total_elapsed}, average running time: {format_timedelta(avg_running_time)}")
    print(f"[SUMMARY] Total configurations run: {successes + failures} (Success: {successes}, Failed: {failures})")
    print(f"{'=' * 70}\n")

    # Telegram: final summary
    send_telegram(tg_cfg,
        f"{'🎉' if failures == 0 else '⚠️'} <b>Batch run complete!</b>\n"
        f"Configs run: {successes + failures} (✅ {successes} / ❌ {failures})\n"
        f"Total time: {total_elapsed}\n"
        f"Avg per config: {format_timedelta(avg_running_time)}"
    )

    # PC beep — fires after everything is done
    beep_done()