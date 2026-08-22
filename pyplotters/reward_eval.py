"""
reward_evaluator.py

Evaluates episodic reward statistics across run configurations within a parent directory.
Outputs a CSV file ("reward-evaluation.csv") with columns:
    configuration, group, min_episodic_reward, max_episodic_reward,
    avg_episodic_reward, std_episodic_reward

Usage examples:
    python reward_evaluator.py -pid ql-p-ms@0
    python reward_evaluator.py -pid ql-p-ms@0 -c 1,3,5-7
    python reward_evaluator.py -pid ql-p-ms@0,ql-p-ms@1 -c 1-10
"""

import argparse
import glob
import json
import logging
import os
import sys
import math

import numpy as np
import pandas as pd

# Allow sibling-package imports when run directly
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.batch_shifter import parse_parent_dir_ids

LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_REPORTS_DIR = r"reports\\skripsi"
PLOT_RESULTS_DIR = r"pyplotters\\plots"

# BASE_REPORTS_DIR = r"D:\Developments+\Java\onesim-rl-data\reports"
# PLOT_RESULTS_DIR = r"D:\Developments+\Java\onesim-rl-data\plots"

OUTPUT_FILENAME = "reward-evaluation.csv"

EVAL_KEYS = [
    "configuration",
    "group",
    "min_episodic_reward",
    "max_episodic_reward",
    "avg_episodic_reward",
    "std_episodic_reward",
    "ci95_episodic_reward",
    "coef_variance_pct",
    "relative_error_pct",
]

# ─────────────────────────────────────────────────────────────────────────────
# Shared helpers (mirrored from persistence_plotter)
# ─────────────────────────────────────────────────────────────────────────────

FAILED_JSON_FILES: list[dict] = []


def check_exists_source_dir(dir_path: str) -> None:
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The base source directory '{dir_path}' does not exist.")


def read_json_file(file_path: str, run_id: str = None):
    """Read a JSON file, returning None (and logging) on any failure."""
    try:
        if os.path.getsize(file_path) == 0:
            _record_failed_json(run_id, file_path, "Empty JSON file")
            return None

        with open(file_path, "r", encoding="utf-8") as fh:
            return json.load(fh)

    except FileNotFoundError:
        _record_failed_json(run_id, file_path, "File not found")
        return None
    except json.JSONDecodeError as exc:
        _record_failed_json(run_id, file_path, f"JSONDecodeError: {exc}")
        return None
    except Exception as exc:
        _record_failed_json(run_id, file_path, f"Unexpected error: {exc}")
        return None


def _record_failed_json(run_id, file_path, error_msg):
    FAILED_JSON_FILES.append({"run_id": run_id, "file": file_path, "error": error_msg})
    log.warning(f"[FAILED JSON] {error_msg}: {file_path}")


def retrieve_episode_json_dirs(run_id_dir: str) -> list[str]:
    """
    Return sorted list of episode JSON file paths under <run_id_dir>/ep/<N>/*.json,
    skipping episode 0 (baseline).
    """
    episodes_dir = glob.glob(os.path.join(run_id_dir, "ep", "*"))

    filtered = []
    for ep_dir in episodes_dir:
        try:
            ep_num = int(os.path.basename(ep_dir))
            if ep_num >= 1:
                filtered.append((ep_num, ep_dir))
        except ValueError:
            pass

    filtered.sort(key=lambda x: x[0])

    total = len(episodes_dir)
    kept = len(filtered)
    log.info(f"Found {kept} training episodes (skipped {total - kept} baseline/non-training).")

    episode_jsons: list[str] = []
    for _, ep_dir in filtered:
        episode_jsons.extend(glob.glob(os.path.join(ep_dir, "*.json")))

    return episode_jsons


def extract_group_from_run_id(run_id: str) -> str:
    """Extract cg@<value> token from run_id; returns 'NA' if absent."""
    for token in run_id.split("-"):
        if "@" in token:
            key, value = token.split("@", 1)
            if key == "cg":
                return value
    return "NA"


# ─────────────────────────────────────────────────────────────────────────────
# Config-index parsing
# ─────────────────────────────────────────────────────────────────────────────

def parse_config_indices(config_string: str) -> list[int]:
    """Parse config indices from a string supporting:
    - Single values: "1,2,9"
    - Ranges: "4-6" (expands to 4,5,6)
    - Mixed: "1,2,4-6,9,10-17"

    Returns sorted list of unique integers.
    Raises ValueError if format is invalid.
    """
    configs: set[int] = set()

    for part in config_string.split(","):
        part = part.strip()

        if "-" in part:
            try:
                start_str, end_str = part.split("-", 1)
                start = int(start_str.strip())
                end = int(end_str.strip())

                if start > end:
                    raise ValueError(f"Invalid range '{part}': start > end")

                configs.update(range(start, end + 1))
            except ValueError as exc:
                raise ValueError(f"Invalid range format '{part}': {exc}") from exc
        else:
            try:
                configs.add(int(part))
            except ValueError:
                raise ValueError(f"Invalid config number '{part}' (must be integer)")

    return sorted(configs)


def _config_index_of(run_id: str) -> int | None:
    """
    Extract the cfg@N integer from a run_id token (e.g. 'cfg@03' → 3).
    Returns None if the token is absent or not an integer.
    """
    for token in run_id.split("-"):
        if "@" in token:
            key, value = token.split("@", 1)
            if key == "cfg":
                try:
                    return int(value)
                except ValueError:
                    return None
    return None


# ─────────────────────────────────────────────────────────────────────────────
# Core evaluation
# ─────────────────────────────────────────────────────────────────────────────

def evaluate_run(run_id_dir: str) -> dict | None:
    """
    Compute episodic reward statistics for a single run directory.

    Returns a dict with EVAL_KEYS, or None if no valid JSON was found.
    """
    run_id = os.path.basename(run_id_dir)
    episode_jsons = retrieve_episode_json_dirs(run_id_dir)

    if not episode_jsons:
        log.warning(f"No episode JSON files found in: {run_id_dir}")
        return None

    episodic_rewards: list[float] = []

    for json_path in episode_jsons:
        json_data = read_json_file(json_path, run_id=run_id)
        if json_data is None:
            continue

        # Each episode JSON is a list of step records; collect currentEpisodeReward
        # from the last step (final accumulated reward for that episode).
        if isinstance(json_data, list):
            for entry in json_data:
                if "currentEpisodeReward" in entry:
                    episodic_rewards.append(float(entry["currentEpisodeReward"]))
                    break  # one value per episode file is sufficient
        elif isinstance(json_data, dict) and "currentEpisodeReward" in json_data:
            episodic_rewards.append(float(json_data["currentEpisodeReward"]))

    if not episodic_rewards:
        log.warning(f"No episodic reward data could be extracted for run: {run_id}")
        return None

    rewards = np.array(episodic_rewards, dtype=float)

    std_reward = (
        float(rewards.std(ddof=1))
        if len(rewards) > 1
        else 0.0
    )

    ci95_reward = (
        1.96 * std_reward / math.sqrt(len(rewards))
        if len(rewards) > 1
        else 0.0
    )

    avg_reward = float(rewards.mean())

    # Relative Error (RE): CI95 expressed as a percentage of |avg|.
    # Coefficient of Variance (CV): Std expressed as a percentage of |avg|.
    # This gives a scale-independent way to judge whether the CI95/std
    # is "large" or "small" relative to the group's own performance level.
    # NOTE: when |avg| is near zero (reward straddles zero), RE becomes
    # numerically unstable/misleading — flagged as NaN rather than a
    # deceptively large or small percentage.
    NEAR_ZERO_AVG_THRESHOLD = 1e-6

    coef_variance_pct = (
        (std_reward / abs(avg_reward)) * 100.0
        if abs(avg_reward) > NEAR_ZERO_AVG_THRESHOLD
        else float("nan")
    )

    relative_error_pct = (
        (ci95_reward / abs(avg_reward)) * 100.0
        if abs(avg_reward) > NEAR_ZERO_AVG_THRESHOLD
        else float("nan")
    )

    return {
        "configuration": run_id,
        "group": extract_group_from_run_id(run_id),
        "min_episodic_reward": float(rewards.min()),
        "max_episodic_reward": float(rewards.max()),
        "avg_episodic_reward": avg_reward,
        "std_episodic_reward": std_reward,
        "ci95_episodic_reward": ci95_reward,
        "coef_variance_pct": coef_variance_pct,
        "relative_error_pct": relative_error_pct,
    }


def process_parent_id(
    parent_id: str,
    config_indices: list[int] | None = None,
) -> pd.DataFrame:
    """
    Walk all run-id directories under BASE_REPORTS_DIR/<parent_id>,
    optionally filtered to those whose cfg@N index is in config_indices.

    Returns a DataFrame with EVAL_KEYS columns (one row per run).
    """
    parent_id_dir = os.path.join(BASE_REPORTS_DIR, parent_id)
    check_exists_source_dir(parent_id_dir)

    run_dirs = glob.glob(os.path.join(parent_id_dir, "run-id", "*"))
    if not run_dirs:
        log.warning(f"No run-id sub-directories found under {parent_id_dir}; falling back to direct subdirectories.")
        run_dirs = glob.glob(os.path.join(parent_id_dir, "*"))

    run_dirs = [d for d in run_dirs if os.path.isdir(d)]

    if not run_dirs:
        log.error(f"No valid run directories found for parent_id: {parent_id}")
        return pd.DataFrame(columns=EVAL_KEYS)

    # Optional cfg@N filtering
    if config_indices is not None:
        config_set = set(config_indices)
        filtered = []
        for rd in run_dirs:
            idx = _config_index_of(os.path.basename(rd))
            if idx is not None and idx in config_set:
                filtered.append(rd)
        log.info(
            f"Config filter applied: {len(filtered)}/{len(run_dirs)} run directories selected "
            f"(indices: {sorted(config_set)})"
        )
        run_dirs = filtered

    if not run_dirs:
        log.warning("No run directories remain after config filtering.")
        return pd.DataFrame(columns=EVAL_KEYS)

    rows: list[dict] = []
    for run_dir in sorted(run_dirs):
        log.info(LINE_LENGTH * "-")
        log.info(f"Evaluating: {run_dir}")
        result = evaluate_run(run_dir)
        if result is not None:
            rows.append(result)

    return pd.DataFrame(rows, columns=EVAL_KEYS)


def save_evaluation_csv(df: pd.DataFrame, parent_id: str) -> str:
    """
    Save the evaluation DataFrame to PLOT_RESULTS_DIR/<parent_id>/reward-evaluation.csv.
    Returns the full output path.
    """
    out_dir = os.path.join(PLOT_RESULTS_DIR, parent_id)
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, OUTPUT_FILENAME)
    df.to_csv(out_path, index=False, sep=";", header=True)
    log.info(f"Saved reward evaluation CSV → {out_path}")
    return out_path


# ─────────────────────────────────────────────────────────────────────────────
# JSON validation summary (mirrored from persistence_plotter)
# ─────────────────────────────────────────────────────────────────────────────

def print_json_validation_summary() -> None:
    print("=" * LINE_LENGTH)
    print("JSON VALIDATION SUMMARY")
    print("=" * LINE_LENGTH)

    json_problem_entries = [e for e in FAILED_JSON_FILES if e["error"] != "File not found"]
    missing_file_entries = [e for e in FAILED_JSON_FILES if e["error"] == "File not found"]

    if not FAILED_JSON_FILES:
        print("All JSON files validated successfully. No issues detected.")
        return

    if json_problem_entries:
        print(f"WARNING: Total failed JSON files: {len(json_problem_entries)}")
        print("-" * LINE_LENGTH)
        grouped = {}
        for entry in json_problem_entries:
            grouped.setdefault(entry["run_id"], []).append(entry)
        for run_id, errors in grouped.items():
            print(f"RUN CONFIG: {run_id}")
            print(f"FAILED FILE COUNT: {len(errors)}")
            for i, err in enumerate(errors, start=1):
                print(f"[{i}] FILE  : {err['file']}")
                print(f"    ERROR : {err['error']}")
            print("-" * LINE_LENGTH)

    if missing_file_entries:
        print()
        print("=" * LINE_LENGTH)
        print("MISSING FILES SUMMARY")
        print("=" * LINE_LENGTH)
        print(f"WARNING: Total missing files: {len(missing_file_entries)}")
        print("-" * LINE_LENGTH)
        grouped = {}
        for entry in missing_file_entries:
            grouped.setdefault(entry["run_id"], []).append(entry)
        for run_id, entries in grouped.items():
            print(f"RUN CONFIG: {run_id}")
            print(f"MISSING FILE COUNT: {len(entries)}")
            for i, entry in enumerate(entries, start=1):
                print(f"[{i}] FILE  : {entry['file']}")
            print("-" * LINE_LENGTH)


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    check_exists_source_dir(BASE_REPORTS_DIR)

    parser = argparse.ArgumentParser(
        description=(
            "ONE Simulator reward evaluator. "
            "Computes min/max/avg/std episodic reward per run and saves a summary CSV."
        )
    )

    parser.add_argument(
        "-pid", "--parent-id", type=str, required=True,
        help=(
            "Parent report source directory/directories, comma-separated. "
            "(e.g. \"ql-p-ms@0\" or \"ql-p-ms@0,ql-p-ms@1\")"
        ),
    )

    parser.add_argument(
        "-c", "--config", type=str, required=False,
        help=(
            "Config indices to filter by (e.g. '1', '1-5', '1,3,5-7'). "
            "Matches the cfg@N token in run directory names. "
            "If not provided, all configs are processed."
        ),
    )

    args = parser.parse_args()

    # Parse -c / --config
    config_indices: list[int] | None = None
    if args.config:
        try:
            config_indices = parse_config_indices(args.config)
            log.info(f"Config filter: {config_indices}")
        except ValueError as exc:
            log.error(f"Invalid -c/--config value: {exc}")
            sys.exit(1)

    # Parse -pid
    parent_dir_ids = parse_parent_dir_ids(args.parent_id)
    if not parent_dir_ids:
        log.error("No valid parent_dir_id(s) provided.")
        sys.exit(1)

    log.info(f"Processing {len(parent_dir_ids)} parent_dir_id(s): {parent_dir_ids}")

    for parent_id in parent_dir_ids:
        log.info(LINE_LENGTH * "=")
        log.info(f"Parent ID: {parent_id}")

        eval_df = process_parent_id(parent_id, config_indices=config_indices)

        if eval_df.empty:
            log.warning(f"No evaluation data produced for parent_id: {parent_id}")
            continue

        out_path = save_evaluation_csv(eval_df, parent_id)

        # Print a quick preview to stdout
        print()
        print(f"{'=' * LINE_LENGTH}")
        print(f"REWARD EVALUATION — {parent_id}")
        print(f"{'=' * LINE_LENGTH}")
        print(eval_df.to_string(index=False))
        print(f"\nSaved → {out_path}")

    print()
    print_json_validation_summary()