import re
import sys
import subprocess

# This python file is used to run one.bat scripts sequentially and label the runs.
# For episodic Q-Learning runs, use run_episodes() instead of run_scripts().

label_placeholder = "IDENTIFIER"

scripts = [
    ".\\one.bat -b 1 -d Report.reportDir=reports/skripsi/bm/run-id/IDENTIFIER@@MovementModel.rngSeed=0 .\\settings\\skripsi\\randomsearch-bm.cfg",
    ".\\one.bat -b 1 -d Report.reportDir=reports/skripsi/rw/run-id/IDENTIFIER@@MovementModel.rngSeed=0 .\\settings\\skripsi\\randomsearch-rw.cfg",
    ".\\one.bat -b 4 -d Report.reportDir=reports/skripsi/levy/run-id/IDENTIFIER@@MovementModel.rngSeed=0 .\\settings\\skripsi\\randomsearch-lf.cfg",
]

# Episodic Q-Learning: each "run" is one episode; the persistence file carries
# Q-table and epsilon forward. Episode number is injected via -d so it appears
# in both the scenario name and the report file names.
default_qlearn_config = ".\\settings\\skripsi\\randomsearch-qlearn.cfg"

qlearn_template = (
    ".\\one.bat -b 1 "
    "-d Report.reportDir=reports/skripsi/qlearn/run-id/IDENTIFIER/ep/EP"
    "@@EpisodicPersistenceManager.persistencePath=reports/skripsi/qlearn/run-id/IDENTIFIER/_persistence.json"
    "@@EpisodicPersistenceManager.episodeNumber=EP "
    f"{default_qlearn_config}"
)
default_lfe_config = ".\\settings\\skripsi\\randomsearch-lf-episodic.cfg"
lfepisodic_template = (
    ".\\one.bat -b 1 "
    "-d Report.reportDir=reports/skripsi/lf-episodic/run-id/IDENTIFIER/ep/EP"
    "-d Report.persistencePath=reports/skripsi/lf-episodic/run-id/IDENTIFIER/_persistence.json"
    "@@EpisodicPersistenceManager.episodeNumber=EP "
    f"{default_lfe_config}"
)

# Characters not allowed in Windows filenames/path components
INVALID_CHARS_RE = re.compile(r'[<>:"/\\|?*]')
WINDOWS_RESERVED_NAMES = {
    "CON", "PRN", "AUX", "NUL",
    "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
    "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
}

def validate_run_id(run_id: str) -> None:
    """
    Validate that run_id is safe to use as a Windows path component.

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


def _run(command: str) -> None:
    """Executes a single one.bat command, printing output and raising on error."""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True,
                                capture_output=True, text=True)
        print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error running: {command}")
        print(f"Return code : {e.returncode}")
        print(f"Error output: {e.stderr}")


def run_scripts(runs: int) -> None:
    """Run baseline (bm / rw / lf) configurations for `runs` independent seeds."""
    for i in range(runs):
        for script in scripts:
            _run(script.replace(label_placeholder, str(i + 1)))


def get_template(config: str) -> str:
    if config == "qlearn":
        return qlearn_template
    elif config == "lfe":
        return lfepisodic_template
    else:
        raise ValueError(f"Unknown config '{config}'. Valid options are 'qlearn' or 'lfe'.")


def run_episodes(config: str, run_id: str, episodes: int) -> None:
    """
    Run `episodes` sequential Q-Learning episodes for a single experiment run.

    Episode numbers are 1-based.  The persistence file is fixed per run so
    that episode N+1 automatically reads what episode N wrote.

    Args:
        config:   Which configuration to run ("qlearn" or "lfe").
        run_id:   Identifier for this overall experiment run (used in path).
        episodes: Number of episodes to execute.
    """
    # Making sure the run_id has no PATH illegal characters
    validate_run_id(run_id)

    settings_to_run = get_template(config)

    for ep in range(1, episodes + 1):
        cmd = (
            settings_to_run
            .replace(label_placeholder, str(run_id))
            .replace("EP", str(ep))
        )
        _run(cmd)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ONE Simulator multi-run/episodic launcher"
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    # Baseline baselines (bm / rw / lf)
    p_baseline = subparsers.add_parser("baseline", help="Run bm/rw/lf baselines")
    p_baseline.add_argument("runs", type=int, help="Number of independent runs")

    # Episodic Q-Learning
    p_episodes = subparsers.add_parser("episodic", help="Run episodic simulations")
    p_episodes.add_argument("config", type=str, help="Configuration to run (qlearn or lfe)")
    p_episodes.add_argument("run_id", type=str, help="Run identifier (used in paths)")
    p_episodes.add_argument("episodes", type=int, help="Number of episodes")

    args = parser.parse_args()

    if args.mode == "baseline":
        run_scripts(args.runs)
    elif args.mode == "episodic":
        run_episodes(args.config, args.run_id, args.episodes)
    else:
        raise ValueError(f"Unknown mode '{args.mode}'. Valid modes are 'baseline' or 'episodic'.")
