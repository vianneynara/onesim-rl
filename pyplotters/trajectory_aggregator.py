"""
Trajectory Aggregator Module

Aggregates trajectoryFrequencies from episodic Persistence JSON files across 
selected episodes using simple division aggregation for scientific empirical plotting.

Method: Each trajectory's average is computed as:
    average = sum_of_frequencies_across_episodes / total_episodes

This approach provides a consistent baseline where:
- Trajectories missing from some episodes are implicitly treated as 0
- Results are directly comparable with other statistical analyses
- Proper scientific representation of expected values per episode

Accepts episode ranges (e.g., "1-5,8,10-15") and validates against available 
episodes in the ep/ subdirectory structure.

Examples:
  # Aggregate all episodes for a run
  python -m pyplotters.trajectory_aggregator -rid ql-c-ms@0-ls@0
  
  # Aggregate specific episodes with custom title
  python -m pyplotters.trajectory_aggregator -rid ql-c-ms@0-ls@0 -eps 1-10,15,20-25 -t "Custom Title"
  
  # Using parent_id with episode selection
  python -m pyplotters.trajectory_aggregator -pid ql-p-ms@0 -eps 1,2,3
"""

import argparse
import glob
import json
import logging
import os
import sys
from typing import Tuple, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MultipleLocator

# Allow running this file as a script while using absolute package imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.batch_shifter import parse_parent_dir_ids

# Configuration
LINE_LENGTH = 100
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s %(levelname)s %(name)s]: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

BASE_REPORTS_DIR = r"D:\Developments+\Java\onesim-rl-data\reports"
PLOT_RESULTS_DIR = r"D:\Developments+\Java\onesim-rl-data\plots"

# Toggle for future CSV export feature
STORE_AS_CSV = False

LIST_OF_IGNORED_OVERRIDES = [
    "cfg",  # config index
    "cg",  # config group
    "ql500",  # Q-Learning with 500 runs
    "mcn500",
    "lfe500"  # Lévy Flight with 500 runs
]

# ===========================================================================================
# UTILITY FUNCTIONS
# ===========================================================================================

def parse_run_description(_run_id: str) -> str:
    """
    Parse run_id into key-value pairs formatted as a description string.
    
    Example: "ql-movseed@0-learnseed@1" -> "(ql; movseed=0; learnseed=1)"
    If no @ delimiters found, returns empty string.
    Filters out keys in LIST_OF_IGNORED_OVERRIDES.
    
    Args:
        _run_id: The run identifier string
        
    Returns:
        Formatted string like "(key1=val1; key2=val2; ...)" or empty string
    """
    tokens = _run_id.split("-")
    parsed_tokens = []
    has_pattern = False

    for token in tokens:
        if "@" in token:
            has_pattern = True
            key, value = token.split("@", 1)
            if key not in LIST_OF_IGNORED_OVERRIDES:
                parsed_tokens.append(f"{key}={value}")
        else:
            # No @ in token, treat as standalone key
            if token not in LIST_OF_IGNORED_OVERRIDES:
                parsed_tokens.append(token)

    # Return empty string if no pattern found (no @ delimiters)
    if not has_pattern:
        return ""

    return f"({'; '.join(parsed_tokens)})"


def parse_episode_range(episode_spec: str) -> List[int]:
    """
    Parse episode specification into a list of episode numbers.
    
    Supports:
    - Single values: "5" -> [5]
    - Ranges: "1-5" -> [1, 2, 3, 4, 5]
    - Mixed: "1-3,5,7-9" -> [1, 2, 3, 5, 7, 8, 9]
    
    Args:
        episode_spec: Comma-separated episode specification
        
    Returns:
        Sorted list of unique episode numbers
        
    Raises:
        ValueError: If specification is invalid
    """
    episodes = set()
    
    if not episode_spec or episode_spec.strip() == "":
        return []
    
    try:
        parts = episode_spec.split(",")
        for part in parts:
            part = part.strip()
            if "-" in part:
                # Range specification
                range_parts = part.split("-")
                if len(range_parts) != 2:
                    raise ValueError(f"Invalid range specification: {part}")
                start, end = int(range_parts[0]), int(range_parts[1])
                if start > end:
                    raise ValueError(f"Invalid range: start ({start}) > end ({end})")
                episodes.update(range(start, end + 1))
            else:
                # Single episode number
                episodes.add(int(part))
    except ValueError as e:
        raise ValueError(f"Failed to parse episode specification '{episode_spec}': {e}")
    
    return sorted(list(episodes))


def auto_detect_episodes(run_dir: str) -> List[int]:
    """
    Auto-detect available episodes from ep/* subdirectory structure.
    
    Note: Episode 0 is excluded as it represents the baseline model, not actual training episodes.
    Only episodes >= 1 are returned.
    
    Args:
        run_dir: The run directory path
        
    Returns:
        Sorted list of available episode numbers (starting from 1)
        
    Raises:
        FileNotFoundError: If ep/ directory doesn't exist
    """
    ep_root = os.path.join(run_dir, "ep")
    
    if not os.path.exists(ep_root):
        raise FileNotFoundError(f"Episode directory not found: {ep_root}")
    
    episode_dirs = glob.glob(os.path.join(ep_root, "*"))
    episodes = []
    
    for ep_dir in episode_dirs:
        if os.path.isdir(ep_dir):
            try:
                ep_num = int(os.path.basename(ep_dir))
                if ep_num >= 1:  # Skip episode 0 (baseline)
                    episodes.append(ep_num)
            except ValueError:
                # Skip non-integer directory names
                pass
    
    return sorted(episodes)


def validate_episodes(available: List[int], requested: List[int]) -> Tuple[bool, List[str]]:
    """
    Validate that all requested episodes are available and contiguous.
    
    Args:
        available: List of available episode numbers
        requested: List of requested episode numbers
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    if not available:
        errors.append("No episodes found in ep/ directory")
        return False, errors
    
    if not requested:
        # No specific request; will use all available
        return True, []
    
    # Check for missing episodes
    available_set = set(available)
    for ep in requested:
        if ep not in available_set:
            errors.append(f"Episode {ep} not found (available: {min(available)}-{max(available)})")
    
    return len(errors) == 0, errors


def read_persistence_json(file_path: str) -> Optional[Dict]:
    """
    Read and parse a Persistence JSON file.
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Parsed JSON dict or None if read failed
    """
    try:
        if os.path.getsize(file_path) == 0:
            log.warning(f"[EMPTY JSON] {file_path}")
            return None
        
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data
    except json.JSONDecodeError as e:
        log.warning(f"[JSON ERROR] Failed to parse {file_path}: {e}")
        return None
    except Exception as e:
        log.warning(f"[ERROR] Failed to read {file_path}: {e}")
        return None


def extract_trajectory_frequencies(json_data: Dict) -> Optional[Dict[str, int]]:
    """
    Extract trajectoryFrequencies from persistence JSON data.
    
    Args:
        json_data: Parsed persistence JSON
        
    Returns:
        Dict mapping trajectory_length (str) to frequency (int), or None if not found
    """
    if json_data is None:
        return None
    
    if "trajectoryFrequencies" not in json_data:
        log.warning("trajectoryFrequencies key not found in persistence data")
        return None
    
    traj_freq = json_data.get("trajectoryFrequencies", {})
    if not traj_freq:
        log.warning("trajectoryFrequencies is empty")
        return None
    
    return traj_freq


def aggregate_trajectory_frequencies(
    run_dir: str,
    episodes: List[int]
) -> Tuple[bool, Dict[str, Dict], str]:
    """
    Aggregate trajectoryFrequencies from multiple episodes using simple division.
    
    For scientific empirical plotting, each trajectory's average is computed by:
    average = sum_of_frequencies / total_episodes
    
    Missing trajectories in some episodes are implicitly treated as 0,
    providing a consistent baseline for statistical comparison.
    
    Args:
        run_dir: Run directory containing ep/ subdirectory
        episodes: List of episode numbers to aggregate
        
    Returns:
        Tuple of (success, aggregated_dict, status_message)
        
    Aggregated dict format:
        {
            "trajectory_length_str": {
                "sum": total_frequency_across_episodes,
                "average": total_frequency / num_total_episodes
            },
            ...
        }
    """
    aggregated = {}
    loaded_episodes = 0
    failed_episodes = []
    total_episodes = len(episodes)
    
    for episode_num in episodes:
        persistence_path = os.path.join(
            run_dir, "ep", str(episode_num),
            f"Persistence-Episode@{episode_num}.json"
        )
        
        if not os.path.exists(persistence_path):
            failed_episodes.append(episode_num)
            continue
        
        json_data = read_persistence_json(persistence_path)
        if json_data is None:
            failed_episodes.append(episode_num)
            continue
        
        traj_freq = extract_trajectory_frequencies(json_data)
        if traj_freq is None:
            failed_episodes.append(episode_num)
            continue
        
        # Accumulate frequencies
        for traj_len_str, frequency in traj_freq.items():
            try:
                freq_val = int(frequency)
            except (ValueError, TypeError):
                log.warning(f"Invalid frequency value for trajectory {traj_len_str}: {frequency}")
                continue
            
            if traj_len_str not in aggregated:
                aggregated[traj_len_str] = {"sum": 0, "average": 0}
            
            aggregated[traj_len_str]["sum"] += freq_val
        
        loaded_episodes += 1
    
    # Compute averages: divide by total episodes (not by episodes-using-key)
    for traj_len_str in aggregated:
        aggregated[traj_len_str]["average"] = aggregated[traj_len_str]["sum"] / total_episodes
    
    # Build status message
    status_msg = f"Loaded {loaded_episodes}/{len(episodes)} episodes"
    if failed_episodes:
        status_msg += f"; failed episodes: {failed_episodes}"
    
    success = loaded_episodes > 0
    return success, aggregated, status_msg


def convert_aggregated_to_dataframe(aggregated: Dict) -> pd.DataFrame:
    """
    Convert aggregated trajectory frequencies to DataFrame for plotting.
    
    Args:
        aggregated: Aggregated dict from aggregate_trajectory_frequencies()
        
    Returns:
        DataFrame with columns: trajectory, sum_frequency, avg_frequency, probability
    """
    records = []
    for traj_len_str, data in aggregated.items():
        try:
            traj_len = int(traj_len_str)
        except ValueError:
            continue
        
        records.append({
            "trajectory": traj_len,
            "sum_frequency": data["sum"],
            "avg_frequency": data["average"]
        })
    
    df = pd.DataFrame(records)
    if len(df) > 0:
        df = df.sort_values(by=["trajectory"], ascending=True).reset_index(drop=True)
        # Calculate probabilities based on average frequencies
        total = df["avg_frequency"].sum()
        if total > 0:
            df["probability"] = df["avg_frequency"] / total
        else:
            df["probability"] = 0
    
    return df


def plot_aggregated_trajectory_distribution(
    df: pd.DataFrame,
    file_path: str,
    title: Optional[str] = None,
    num_episodes: int = 0,
    x_max: int = 500,
    logarithmic_x: bool = False,
    _description: str = None
):
    """
    Plot aggregated trajectory distribution.
    
    Similar to persistence_plotter's plot_trajectoryDistribution but adapted for aggregated data.
    
    Args:
        df: DataFrame with trajectory and probability columns
        file_path: Output PNG file path
        title: Custom title (optional)
        num_episodes: Number of episodes aggregated (for subtitle)
        x_max: Maximum X-axis value
        logarithmic_x: Whether to use logarithmic X-axis
        _description: Description string to display under title (optional)
    """
    if len(df) == 0:
        log.warning("Empty DataFrame; skipping plot")
        return
    
    plt.figure(figsize=(12, 6))
    
    # Ensure numeric dtypes
    df = df.copy()
    df["trajectory"] = df["trajectory"].astype(int)
    df["probability"] = df["probability"].astype(float)
    
    # Compute summary statistics
    max_len = int(df["trajectory"].max()) if len(df) > 0 else 0
    mean_len = float((df["trajectory"] * df["probability"]).sum()) if len(df) > 0 else 0
    max_p = float(df["probability"].max()) if len(df) > 0 else 0
    mode_len = int(df.loc[df["probability"] == max_p, "trajectory"].min()) if max_p > 0 else 0
    
    suptitle_y = 0.98
    
    # Plot
    sns.lineplot(data=df, x="trajectory", y="probability", label="Probability (PMF)", linewidth=2)
    
    # Construct title with subtitle
    title_parts = [title or "Average Trajectory Distribution"]
    if num_episodes > 0:
        title_parts.append(f"({num_episodes} episodes)")
    else:
        suptitle_y -= 0.03
    
    final_title = "\n".join(title_parts)
    
    fig = plt.gcf()
    fig.suptitle(final_title, fontweight='bold', fontsize=12, y=suptitle_y)
    
    # Add description as lighter text if present
    if _description:
        fig.text(0.5, 0.91, _description, ha='center', va='top',
                 fontsize=9, fontweight='light', style='italic', color='gray')
        # Adjust top margin to accommodate both title and description
        fig.subplots_adjust(top=0.88)
    else:
        # Adjust top margin for title only
        fig.subplots_adjust(top=0.92)
    
    ax = plt.gca()
    plt.xlabel("Trajectory Length")
    plt.ylabel("Probability / Density")
    ax.set_xlim(1, x_max)
    ax.xaxis.set_major_locator(MultipleLocator(50))
    ax.xaxis.set_minor_locator(MultipleLocator(10))
    plt.gca().set_yticks(np.arange(0, 1.1, 0.1))
    plt.margins(x=0)
    
    # Add summary stats to legend
    handles, labels = ax.get_legend_handles_labels()
    if max_len > 0:
        from matplotlib.lines import Line2D
        stat_lines = [
            f"{'Max trajectory':<20}: {max_len:>6d}",
            f"{'Highest PMF':<20}: {max_p:>10.3f}",
            f"{'Mean length (PMF)':<20}: {mean_len:>10.2f}",
            f"{'Most probable (mode)':<20}: {mode_len:>6d}",
        ]
        handles.extend([Line2D([], [], linestyle='none', color='none', label=s) for s in stat_lines])
    
    ax.legend(handles=handles, loc="best", prop={'family': 'monospace'})
    
    # Save plot
    out_dir = os.path.dirname(file_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    plt.savefig(file_path, bbox_inches='tight', dpi=100)
    plt.close()
    
    log.info(f"Saved plot: {file_path}")


def save_aggregated_data_json(
    aggregated: Dict,
    file_path: str,
    episodes: List[int]
):
    """
    Save aggregated trajectory frequencies as JSON.
    
    Args:
        aggregated: Aggregated dict from aggregate_trajectory_frequencies()
        file_path: Output JSON file path
        episodes: List of episodes aggregated
    """
    output = {
        "metadata": {
            "episodes_aggregated": episodes,
            "num_episodes": len(episodes),
            "format": "aggregated_trajectory_frequencies"
        },
        "aggregated_data": aggregated
    }
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=4, sort_keys=True)
        log.info(f"Saved aggregated data JSON: {file_path}")
    except Exception as e:
        log.error(f"Failed to save aggregated data JSON: {e}")


def save_aggregated_data_csv(
    df: pd.DataFrame,
    file_path: str,
    episodes: List[int]
):
    """
    Save aggregated trajectory frequencies as CSV.
    
    Args:
        df: DataFrame from convert_aggregated_to_dataframe()
        file_path: Output CSV file path
        episodes: List of episodes aggregated
    """
    try:
        # Add metadata as comments at the top
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# Episodes aggregated: {episodes}\n")
            f.write(f"# Total episodes: {len(episodes)}\n")
        
        # Append data
        df.to_csv(file_path, index=False, sep=";", header=True, mode='a')
        log.info(f"Saved aggregated data CSV: {file_path}")
    except Exception as e:
        log.error(f"Failed to save aggregated data CSV: {e}")


def check_exists_source_dir(dir_path):
    """Validate that a directory exists."""
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The base source directory {dir_path} does not exist.")


def process_run_aggregation(
    run_dir: str,
    run_id: str,
    parent_id: Optional[str],
    episodes: List[int],
    title: Optional[str],
    _describe: bool = False
) -> bool:
    """
    Process trajectory aggregation for a single run.
    
    Args:
        run_dir: Full path to run directory
        run_id: Run identifier (for logging)
        parent_id: Parent directory ID (for output path)
        episodes: List of episode numbers to aggregate
        title: Custom plot title
        _describe: Whether to add run description to plot
        
    Returns:
        True if successful, False otherwise
    """
    log.info("=" * LINE_LENGTH)
    log.info(f"Processing run: {run_id}")
    log.info("=" * LINE_LENGTH)
    
    # Auto-detect episodes if not specified
    if not episodes:
        try:
            available = auto_detect_episodes(run_dir)
            log.info(f"Auto-detected {len(available)} episodes: {available[0]}-{available[-1]}")
            episodes = available
        except FileNotFoundError as e:
            log.error(f"Failed to auto-detect episodes: {e}")
            return False
    
    # Validate episodes
    try:
        available = auto_detect_episodes(run_dir)
    except FileNotFoundError as e:
        log.error(f"Cannot access episode directory: {e}")
        return False
    
    is_valid, errors = validate_episodes(available, episodes)
    if not is_valid:
        for error in errors:
            log.error(error)
        log.error("Exiting due to missing episodes")
        return False
    
    log.info(f"Aggregating {len(episodes)} episodes: {episodes}")
    
    # Aggregate trajectoryFrequencies
    success, aggregated, status_msg = aggregate_trajectory_frequencies(run_dir, episodes)
    log.info(status_msg)
    
    if not success or not aggregated:
        log.error("Failed to aggregate trajectory frequencies")
        return False
    
    # Convert to DataFrame and plot
    df = convert_aggregated_to_dataframe(aggregated)
    
    if len(df) == 0:
        log.error("No valid trajectory data to plot")
        return False
    
    # Output directory: pyplotters/plots[/<parent>]/<run_id>/
    parent_results_dir = os.path.join(PLOT_RESULTS_DIR, parent_id) if parent_id else PLOT_RESULTS_DIR
    run_out_dir = os.path.join(parent_results_dir, run_id)
    os.makedirs(run_out_dir, exist_ok=True)
    
    # Generate description if --describe flag is set
    _description = parse_run_description(run_id) if _describe else None
    
    # Save plot
    plot_file = os.path.join(run_out_dir, f"Average Trajectory Distribution (of {len(episodes)} episodes).png")
    plot_aggregated_trajectory_distribution(
        df,
        plot_file,
        title=title,
        num_episodes=len(episodes),
        _description=_description
    )
    
    # Save aggregated data as JSON
    json_file = os.path.join(run_out_dir, "aggregated_trajectory_frequencies.json")
    save_aggregated_data_json(aggregated, json_file, episodes)
    
    # Optionally save as CSV
    if STORE_AS_CSV:
        csv_file = os.path.join(run_out_dir, "aggregated_trajectory_frequencies.csv")
        save_aggregated_data_csv(df, csv_file, episodes)
    
    log.info(f"Successfully processed run: {run_id}")
    return True


# ===========================================================================================
# MAIN
# ===========================================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Aggregate trajectory frequencies from multiple episodes and generate plots"
    )
    
    parser.add_argument(
        "-pid", "--parent-id", type=str,
        help="Parent report source directory/directories, comma-separated (e.g., 'ql' or 'ql-p-ms@0,ql-p-ms@1')"
    )
    
    parser.add_argument(
        "-rid", "--run_id", type=str,
        help="Run ID directory (e.g., 'ql-c-ms@0-ls@0')"
    )
    
    parser.add_argument(
        "-t", "--title", type=str,
        help="Custom title for plots"
    )
    
    parser.add_argument(
        "-d", "--describe", action="store_true",
        help="Parse run_id and add description to plots (reserved for future use)"
    )
    
    parser.add_argument(
        "-eps", "--episodes", type=str, default=None,
        help="Episode range specification: single values, ranges, or mixed (e.g., '1-5,8,10-15'). "
             "Defaults to all available episodes if not specified."
    )
    
    args = parser.parse_args()
    
    if not args.parent_id and not args.run_id:
        parser.print_help()
        sys.exit()
    
    # Parse episode specification
    requested_episodes = []
    if args.episodes:
        try:
            requested_episodes = parse_episode_range(args.episodes)
            log.info(f"Requested episodes: {requested_episodes}")
        except ValueError as e:
            log.error(f"Invalid episode specification: {e}")
            sys.exit(1)
    
    check_exists_source_dir(BASE_REPORTS_DIR)
    
    # Process parent_id(s)
    if args.parent_id:
        parent_dir_ids = parse_parent_dir_ids(args.parent_id)
        
        if not parent_dir_ids:
            log.error("No valid parent_dir_id(s) provided")
            sys.exit(1)
        
        log.info(f"Processing {len(parent_dir_ids)} parent_dir_id(s): {parent_dir_ids}")
        
        for parent_id in parent_dir_ids:
            parent_id_dir = os.path.join(BASE_REPORTS_DIR, parent_id)
            check_exists_source_dir(parent_id_dir)
            
            run_dirs = glob.glob(os.path.join(parent_id_dir, "run-id", "*"))
            if not run_dirs:
                log.info("No run-id directories found; checking for direct subdirectories")
                run_dirs = glob.glob(os.path.join(parent_id_dir, "*"))
            
            os.makedirs(os.path.join(PLOT_RESULTS_DIR, parent_id), exist_ok=True)
            
            for run_dir in run_dirs:
                if os.path.isdir(run_dir):
                    run_id = os.path.basename(run_dir)
                    process_run_aggregation(
                        run_dir,
                        run_id,
                        parent_id,
                        requested_episodes,
                        args.title,
                        args.describe
                    )
    
    elif args.run_id:
        # Find run_id in BASE_REPORTS_DIR
        run_dir = None
        
        for root, dirs, files in os.walk(BASE_REPORTS_DIR):
            for dir_name in dirs:
                if dir_name == args.run_id:
                    run_dir = os.path.join(root, dir_name)
                    break
        
        if not run_dir:
            log.error(f"The run-id '{args.run_id}' not found")
            sys.exit(1)
        
        check_exists_source_dir(run_dir)
        process_run_aggregation(
            run_dir,
            args.run_id,
            None,
            requested_episodes,
            args.title,
            args.describe
        )
    
    log.info("=" * LINE_LENGTH)
    log.info("Trajectory aggregation complete")
    log.info("=" * LINE_LENGTH)


if __name__ == "__main__":
    main()

