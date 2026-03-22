import re
import sys
import subprocess

# This python file is used to run one.bat scripts sequentially and label the runs.
# For episodic Q-Learning runs, use run_episodes() instead of run_scripts().

label_placeholder = "NUM"

scripts = [
    ".\\one.bat -b 1 -d Report.reportDir=reports/skripsi/bm/run/NUM@@MovementModel.rngSeed=0 .\\settings\\skripsi\\randomsearch-bm.cfg",
    ".\\one.bat -b 1 -d Report.reportDir=reports/skripsi/rw/run/NUM@@MovementModel.rngSeed=0 .\\settings\\skripsi\\randomsearch-rw.cfg",
    ".\\one.bat -b 4 -d Report.reportDir=reports/skripsi/levy/run/NUM@@MovementModel.rngSeed=0 .\\settings\\skripsi\\randomsearch-lf.cfg",
]

# Episodic Q-Learning: each "run" is one episode; the persistence file carries
# Q-table and epsilon forward. Episode number is injected via -d so it appears
# in both the scenario name and the report file names.
qlearn_template = (
    ".\\one.bat -b 1 "
    "-d Report.reportDir=reports/skripsi/qlearn/run/NUM/ep/EP"
    "@@EpisodicPersistenceManager.episodeNumber=EP "
    ".\\settings\\skripsi\\randomsearch-qlearn.cfg"
)

# Characters not allowed in Windows filenames/path components
INVALID_CHARS_RE = re.compile(r'[<>:"/\\|?*]')

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


def run_episodes(run_id: str, episodes: int) -> None:
    """
    Run `episodes` sequential Q-Learning episodes for a single experiment run.

    Episode numbers are 1-based.  The persistence file is fixed per run so
    that episode N+1 automatically reads what episode N wrote.

    Args:
        run_id:   Identifier for this overall experiment run (used in path).
        episodes: Number of episodes to execute.
    """
    # Making sure the run_id has no PATH illegal characters
    validate_run_id(run_id)

    for ep in range(1, episodes + 1):
        cmd = (
            qlearn_template
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
    p_episodes = subparsers.add_parser("qlearn", help="Run episodic Q-Learning")
    p_episodes.add_argument("run_id", type=str, help="Run identifier (used in paths)")
    p_episodes.add_argument("episodes", type=int, help="Number of episodes")

    args = parser.parse_args()

    if args.mode == "baseline":
        run_scripts(args.runs)
    elif args.mode == "qlearn":
        run_episodes(args.run_id, args.episodes)

