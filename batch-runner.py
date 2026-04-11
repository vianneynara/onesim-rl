"""
The second version of batch runner, will provide better and more flexible runs.
"""

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


# ------------------------------------------------------------------------------------------------------------------- #
# BATCH RUNNER
# ------------------------------------------------------------------------------------------------------------------- #

import re
import sys
import subprocess

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
        ""
    }
]

def run_script(algo: str, overrides: str = None, ep: int = -1) -> bool:
    _current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"[{_current_time}] Running episode {ep} for algorithm {algo}.")
    print(f"[{_current_time}] ============================================================")

    script = [
        r".\one.bat",
        "-b", "1",
        "-d", overrides,
        alg_base_settings[algo]
    ]

    try:
        subprocess.run(script, check=True, shell=True)
        return True
    except subprocess.CalledProcessError:
        print(f"[{_current_time}] Error running episode {ep} for algorithm {algo}.")
        return False

if __name__ == "__main__":
    import argoarse

    parser = argparse.ArgumentParser(
        description="ONE Simulator multi-run/episodic launcher (version 2)"
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # [ baseline runners, we skip this rn ]
    p_baseline = subparsers.add_parser("baseline", help="Run baseline algorithms")

    # [ episodic runners ]
    p_episodes = subparsers.add_parser("episodic", help="Run episodic simulations")
    p_episodes.add_argument("config_index", type=int, help="index of the config to run (from 0)")
    p_episodes.add_argument("run_id", type=str, help="Run identifier (used in paths), generated if empty")
    p_episodes.add_argument("episodes", type=int, help="Number of episodes")