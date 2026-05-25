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

Three modes of operation:
1. Standard -pid/-rid mode: Process selected runs (with optional config filtering)
2. Config filtering (-c): Process only specified configs (e.g., "1-5", "1,3,5-7")
3. Compare-all (--compareall): Aggregate and compare trajectory distributions across all configs

Examples:
  # Aggregate all episodes for a run
  python -m pyplotters.trajectory_aggregator -rid ql-c-ms@0-ls@0
  
  # Aggregate specific episodes with custom title
  python -m pyplotters.trajectory_aggregator -rid ql-c-ms@0-ls@0 -eps 1-10,15,20-25 -t "Custom Title"
  
  # Using parent_id with episode selection
  python -m pyplotters.trajectory_aggregator -pid ql-p-ms@0 -eps 1,2,3
  
  # Filter by specific configs
  python -m pyplotters.trajectory_aggregator -pid ql-p-ms@0 -c 1-5,10-15
  
  # Compare-all mode: aggregate trajectories across configs and generate comparison plot
  python -m pyplotters.trajectory_aggregator -pid ql-p-ms@0 --compareall
  
  # Compare-all with config filtering and episodes
  python -m pyplotters.trajectory_aggregator -pid ql-p-ms@0 --compareall -c 1-5,18-23 -eps 1-50
"""

import argparse
import glob
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from typing import Tuple, Dict, List, Optional, Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.ticker import MultipleLocator, LogLocator, LogFormatterSciNotation

# Allow running this file as a script while using absolute package imports
if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pyrunner.batch_shifter import parse_parent_dir_ids
from pyplotters.term_dictionary import GROUP_VALUE_TERMS, CONFIG_GROUP_TERMS

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
    "cfg",  # config index (e.g., cfg@01)
    "cg",   # config group (e.g., cg@ql_epsilon)
    "qlm_pt",  # paused trining (e.g., qlm_pt@True)
    "qlm_rth",  # reset trajectory history (e.g., qlm_rth@True)
    "mcnm_pt",  # paused trining (e.g., mcnm_pt@True)
    "mcnm_rth",  # reset trajectory history (e.g., mcnm_rth@True)
    "lfe_rth",  # reset trajectory history (e.g., lfe_rth@True)
    "ql500",  # Q-Learning with 500 runs
    "mcn500",
    "lfe500",  # Lévy Flight with 500 runs
    "ql10",
    "lfe10",
]

BESTOF_CMAP = "bright"

# Line styles matching bestof_plotter for consistent visualization across configs
LINE_STYLES = ["-", "--", "-.", ":"]

# ===========================================================================================
# UTILITY FUNCTIONS
# ===========================================================================================

@dataclass(frozen=True)
class ParsedRunId:
    run_id: str
    tokens: dict[str, str]


def _exit_with_warning(msg: str, code: int = 2) -> None:
    """Exit with a warning message."""
    log.warning(msg)
    raise SystemExit(code)


def parse_run_id_strict(run_id: str) -> ParsedRunId:
    """Parse a run-id directory name.

    Expected format: <prefix>-<key>@<value>-<key>@<value>...

    Notes:
    - The first dash-separated component is treated as prefix and ignored.
    - All remaining components *must* contain exactly one '@' and non-empty key/value.
    """
    parts = run_id.split("-")
    if len(parts) < 2:
        _exit_with_warning(
            f"Run-id '{run_id}' does not match expected format: <prefix>-<key>@<value>-..."
        )

    tokens: dict[str, str] = {}
    for raw in parts[1:]:
        if raw.count("@") != 1:
            log.warn(
                f"Run-id '{run_id}' contains invalid token '{raw}'. Expected exactly one '@'."
            )
            log.info(f"Skipping the token {raw}")
            continue
        k, v = raw.split("@")
        if not k or not v:
            _exit_with_warning(
                f"Run-id '{run_id}' contains empty key/value in token '{raw}'."
            )
        if k in tokens:
            _exit_with_warning(
                f"Run-id '{run_id}' contains duplicate key '{k}'. This tool requires unique keys."
            )
        tokens[k] = v

    return ParsedRunId(run_id=run_id, tokens=tokens)


def extract_cfg_index(folder_name: str) -> Optional[int]:
    """Extract cfg index from folder name like 'cfg@05-ql500-...'.
    
    Returns the integer index (1-based) or None if not found.
    """
    match = re.match(r"cfg@(\d+)", folder_name)
    if match:
        try:
            return int(match.group(1))
        except ValueError:
            pass
    return None


def extract_cg_value(folder_name: str) -> Optional[str]:
    """Extract config group value from run_id pattern like 'cg@lf-...'

    Example: "cfg@36-cg@lf-lfe10-lfe_la@0.25" → "lf"
    """
    # Match cg@ followed by any characters until - or @ or end of string
    match = re.search(r"cg@([^-@]+)", folder_name)
    if match:
        return match.group(1)
    return None


def parse_config_indices(config_string: str) -> list[int]:
    """Parse config indices from a string supporting:
    - Single values: "1,2,9"
    - Ranges: "4-6" (expands to 4,5,6)
    - Mixed: "1,2,4-6,9,10-17"
    
    Returns sorted list of unique integers.
    Raises ValueError if format is invalid.
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
                    raise ValueError(f"Invalid range '{part}', start > end")
                
                # Add all values in range (inclusive)
                for i in range(start, end + 1):
                    configs.add(i)
            except ValueError as e:
                raise ValueError(f"Invalid range format '{part}': {e}")
        else:
            # It's a single value
            try:
                configs.add(int(part))
            except ValueError:
                raise ValueError(f"Invalid config number '{part}' (must be integer)")
    
    return sorted(list(configs))


def filter_summary_by_configs(summary_df: pd.DataFrame, config_indices: list[int]) -> pd.DataFrame:
    """Filter summary DataFrame to include only rows matching specified config indices.
    
    Matches configuration_directory entries starting with 'cfg@N' where N is in config_indices.
    
    Args:
        summary_df: DataFrame with 'configuration_directory' column
        config_indices: List of integer config indices to include (1-based)
    
    Returns:
        Filtered DataFrame with only matching rows
    """
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")
    
    # Track which configs were requested but not found
    requested_indices = set(config_indices)
    found_indices = set()
    
    # Filter rows by matching cfg@ index
    mask = pd.Series([False] * len(summary_df), index=summary_df.index)
    for idx, row in summary_df.iterrows():
        config_dir = str(row["configuration_directory"])
        cfg_idx = extract_cfg_index(config_dir)
        
        if cfg_idx is not None and cfg_idx in config_indices:
            mask.iloc[idx] = True
            found_indices.add(cfg_idx)
    
    filtered_df = summary_df[mask]
    
    # Warn about missing configs
    missing_indices = requested_indices - found_indices
    if missing_indices:
        for cfg_idx in sorted(missing_indices):
            log.warning(
                f"Requested config cfg@{cfg_idx} not found in summary.csv. Skipping."
            )
    
    if len(filtered_df) == 0:
        _exit_with_warning(
            f"No runs found matching requested configs: {sorted(config_indices)}"
        )
    
    log.info(f"Filtered to {len(filtered_df)} runs from configs: {sorted(found_indices)}")
    return filtered_df


def key_to_abbr(key: str) -> str:
    """Convert an override key to its abbreviation.

    Example: "ucb_ec" -> "ec" (substring after last underscore)
             "ps_iv"  -> "iv"
             "foo"    -> "foo"
    """
    if "_" in key:
        return key.rsplit("_", 1)[-1]
    return key


def build_legend_label(group_value: str, overrides: dict[str, str]) -> str:
    """Build legend label in the form: '<group> (abbr=value, abbr=value)'.

    Overrides are sorted by abbreviation for stable legends.
    """
    # Expand group value with formal wording when available.
    group_display = GROUP_VALUE_TERMS.get(group_value, group_value)

    items: list[tuple[str, str]] = []
    for k, v in overrides.items():
        items.append((key_to_abbr(k), str(v)))
    items.sort(key=lambda t: t[0])

    overrides_str = ", ".join([f"{abbr}={val}" for abbr, val in items])
    return f'{group_display} {"("+overrides_str+")" if overrides_str else ""}'


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


def _create_trajectory_plot(
    ax,
    df: pd.DataFrame,
    use_log_scale: bool = False,
    x_max: int = 500
):
    """
    Core plotting logic for trajectory distribution.
    
    Args:
        ax: Matplotlib axes object
        df: DataFrame with trajectory and probability columns
        use_log_scale: If True, use logarithmic X-axis (semilogx); otherwise use linear
        x_max: Maximum X-axis value
    """
    if use_log_scale:
        # Logarithmic X-axis plot using semilogx
        ax.semilogx(df["trajectory"], df["probability"], linewidth=2.5, color='purple',
                    label="Probability (PMF)", marker='o' if len(df) < 5 else '', markersize=6, alpha=0.8)
        ax.fill_between(df["trajectory"], df["probability"], alpha=0.2, color='skyblue')
        
        # Configure log-scale X-axis
        ax.xaxis.set_major_locator(LogLocator(base=10, numticks=10))
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
        ax.xaxis.set_major_formatter(LogFormatterSciNotation(base=10))
        ax.set_xlabel("Step Length $l$ (log scale)", fontsize=12, fontweight='bold')
    else:
        # Linear X-axis plot
        sns.lineplot(ax=ax, data=df, x="trajectory", y="probability", color='purple',
                    label="Probability (PMF)", linewidth=2)
        
        # Add scatter plot overlay to show data points only if dataframe has less than 5 rows
        if len(df) < 5:
            sns.scatterplot(ax=ax, data=df, x="trajectory", y="probability", s=15, marker='o', 
                           color='darkblue', alpha=0.7, edgecolor='navy', linewidth=1.5, 
                           zorder=5, legend=False)
        
        # Add horizontal pointer lines from each point to the Y-axis
        for idx, row in df.iterrows():
            x_val = row["trajectory"]
            y_val = row["probability"]
            ax.plot([0, x_val], [y_val, y_val], 'gray', linewidth=0.8, color='gray', alpha=0.4,
                   linestyle='--', zorder=1)
        
        # Configure linear X-axis
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.xaxis.set_minor_locator(MultipleLocator(10))
        ax.set_xlabel("Trajectory Length", fontsize=12, fontweight='bold')
    
    # Common Y-axis configuration
    ax.set_ylabel("Probability Density $P(l)$", fontsize=12, fontweight='bold')
    ax.set_xlim(1, x_max)
    ax.set_ylim(0, ax.get_ylim()[1] * 1.1)
    ax.grid(True, alpha=0.5, which='both', linestyle='--')
    ax.margins(x=0)


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
    Plot aggregated trajectory distribution in both linear and logarithmic scales.
    
    Generates two plots by default:
    1. Linear X-axis plot (standard distribution visualization)
    2. Logarithmic X-axis plot (power-law behavior visualization)
    
    Args:
        df: DataFrame with trajectory and probability columns
        file_path: Output PNG file path (base name; will be modified for log variant)
        title: Custom title (optional)
        num_episodes: Number of episodes aggregated (for subtitle)
        x_max: Maximum X-axis value
        logarithmic_x: Whether to generate logarithmic plots (default True; generates both)
        _description: Description string to display under title (optional)
    """
    if len(df) == 0:
        log.warning("Empty DataFrame; skipping plot")
        return
    
    # Ensure numeric dtypes
    df = df.copy()
    df["trajectory"] = df["trajectory"].astype(int)
    df["probability"] = df["probability"].astype(float)
    
    # Compute summary statistics
    max_len = int(df["trajectory"].max()) if len(df) > 0 else 0
    mean_len = float((df["trajectory"] * df["probability"]).sum()) if len(df) > 0 else 0
    max_p = float(df["probability"].max()) if len(df) > 0 else 0
    mode_len = int(df.loc[df["probability"] == max_p, "trajectory"].min()) if max_p > 0 else 0
    
    # Construct title with subtitle
    title_parts = [title or "Average Trajectory Distribution"]
    if num_episodes > 0:
        title_parts.append(f"({num_episodes} episodes)")
    
    final_title = "\n".join(title_parts)
    
    suptitle_y = 0.98 if num_episodes > 0 else 0.95
    
    # Build summary stats for legend with programmatic fixed-width formatting
    from matplotlib.lines import Line2D
    total_sum = int(df["sum_frequency"].sum()) if "sum_frequency" in df.columns else 0
    
    stat_data = [
        ('Max trajectory', f'{max_len}'),
        ('Highest PMF', f'{max_p:.3f}'),
        ('Mean length (PMF)', f'{mean_len:.2f}'),
        ('Most probable (mode)', f'{mode_len}'),
        ('Sum of all', f'{total_sum}'),
    ]
    
    # Find max key length for alignment
    max_key_len = max(len(key) for key, _ in stat_data)
    
    # Format entries with padding
    stat_lines = [f'{key.ljust(max_key_len)} : {value}' for key, value in stat_data]
    
    # ===== PLOT 1: LINEAR X-AXIS =====
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    
    _create_trajectory_plot(ax, df, use_log_scale=False, x_max=x_max)
    
    fig.suptitle(final_title, fontweight='bold', fontsize=12, y=suptitle_y)
    
    if _description:
        fig.text(0.5, 0.91, _description, ha='center', va='top',
                fontsize=9, fontweight='light', style='italic', color='gray')
        fig.subplots_adjust(top=0.88)
    else:
        fig.subplots_adjust(top=0.92)
    
    # Add stats to legend
    handles, labels = ax.get_legend_handles_labels()
    handles.extend([Line2D([], [], linestyle='none', color='none', label=s) for s in stat_lines])
    ax.legend(handles=handles, loc="best", prop={'family': 'monospace'})
    
    # Save linear plot
    out_dir = os.path.dirname(file_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    
    plt.tight_layout()
    plt.savefig(file_path, bbox_inches='tight', dpi=100)
    plt.close()
    log.info(f"Saved plot: {file_path}")
    
    # ===== PLOT 2: LOGARITHMIC X-AXIS (if enabled) =====
    if logarithmic_x or True:  # Always generate logarithmic plot
        fig = plt.figure(figsize=(12, 6))
        ax = fig.add_subplot(111)
        
        _create_trajectory_plot(ax, df, use_log_scale=True, x_max=x_max)
        
        # Modify title for logarithmic variant
        log_title_parts = [title or "Average Trajectory Distribution"]
        if num_episodes > 0:
            log_title_parts.insert(1, f"({num_episodes} episodes)")
        
        log_final_title = "\n".join(log_title_parts)
        log_final_title += " (logarithmic X scale)"
        fig.suptitle(log_final_title, fontweight='bold', fontsize=12, y=suptitle_y)
        
        if _description:
            fig.text(0.5, 0.91, _description, ha='center', va='top',
                    fontsize=9, fontweight='light', style='italic', color='gray')
            fig.subplots_adjust(top=0.88)
        else:
            fig.subplots_adjust(top=0.92)
        
        # Add stats to legend
        handles, labels = ax.get_legend_handles_labels()
        handles.extend([Line2D([], [], linestyle='none', color='none', label=s) for s in stat_lines])
        ax.legend(handles=handles, loc="best", prop={'family': 'monospace'})
        
        # Save logarithmic plot with modified filename
        base_path = os.path.splitext(file_path)[0]
        ext = os.path.splitext(file_path)[1]
        log_file_path = f"{base_path} (Log Scale X){ext}"
        
        plt.tight_layout()
        plt.savefig(log_file_path, bbox_inches='tight', dpi=100)
        plt.close()
        log.info(f"Saved plot: {log_file_path}")


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
    # Calculate total sum across all trajectories
    total_sum = sum(data.get("sum", 0) for data in aggregated.values())
    
    output = {
        "metadata": {
            "episodes_aggregated": episodes,
            "num_episodes": len(episodes),
            "format": "aggregated_trajectory_frequencies",
            "total_sum": total_sum
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


def run_compareall(
    parent_id: str,
    episodes: List[int] = None,
    suptitle: str = None,
    config_indices: Union[list[int], None] = None
) -> None:
    """Compare aggregated trajectory distributions across all configs in a parent_id.
    
    Loads summary.csv from parent results directory, filters by config indices if specified,
    and generates aggregated trajectory distribution plots for each matching config.
    
    Args:
        parent_id: Parent results directory under pyplotters/plots (must have summary.csv)
        episodes: List of episode numbers to aggregate (auto-detect if empty)
        suptitle: Optional custom title for plots
        config_indices: Optional list of config indices to filter by
    """
    out_dir = os.path.join(PLOT_RESULTS_DIR, parent_id)
    summary_path = os.path.join(out_dir, "summary.csv")

    if not os.path.exists(out_dir):
        _exit_with_warning(
            f"Directory does not exist: {out_dir}. Did you run persistence_plotter.py -pid first?"
        )
    if not os.path.exists(summary_path):
        _exit_with_warning(
            f"Missing {summary_path}. Did you run persistence_plotter.py -pid first?"
        )

    summary_df = pd.read_csv(summary_path, sep=";")
    
    # Apply config filtering if specified
    if config_indices is not None:
        summary_df = filter_summary_by_configs(summary_df, config_indices)
    
    # Ensure required columns exist
    if "configuration_directory" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'configuration_directory'.")
    if "last_episode_cumulative_reward" not in summary_df.columns:
        _exit_with_warning("summary.csv missing required column 'last_episode_cumulative_reward'.")

    # Convert reward to numeric and sort by reward (descending)
    summary_df = summary_df.copy()
    summary_df["last_episode_cumulative_reward"] = pd.to_numeric(
        summary_df["last_episode_cumulative_reward"], errors="coerce"
    )
    if summary_df["last_episode_cumulative_reward"].isna().any():
        _exit_with_warning("summary.csv contains non-numeric last_episode_cumulative_reward values; aborting.")
    
    summary_df = summary_df.sort_values(
        by="last_episode_cumulative_reward",
        ascending=False,
        kind="mergesort"
    )
    
    log.info(LINE_LENGTH * "-")
    log.info(f"Compare-All mode: aggregating trajectory distributions for {len(summary_df)} configs")
    
    # Process each run
    aggregated_dataframes: list[tuple[int, str, dict, int, pd.DataFrame, Optional[str]]] = []
    
    for rank, (_, row) in enumerate(summary_df.iterrows(), start=1):
        run_id = str(row["configuration_directory"])
        reward = row['last_episode_cumulative_reward']
        config_group = None
        
        # Build label showing "Rank: #N, Profile <0N>: $(<overrides>)$"
        try:
            pr = parse_run_id_strict(run_id)
            cfg_num = extract_cfg_index(run_id)
            config_group = extract_cg_value(run_id)
            log.info(f"Processing run {rank}: {run_id} (Profile {cfg_num}, {config_group})")

            # Grab the config group 'cg' key (cg@<config_group>) from pr.tokens
            config_group_str = CONFIG_GROUP_TERMS.get(config_group, "N/A") if config_group else "N/A"
            
            # Extract parameter overrides (exclude cfg, cg, algorithm identifiers)
            overrides = {k: v for k, v in pr.tokens.items() 
                        if k not in LIST_OF_IGNORED_OVERRIDES}
            
            # Build formatted label for subplot title with rank (2-line format)
            if cfg_num is not None:
                if overrides:
                    items: list[tuple[str, str]] = []
                    for k, v in overrides.items():
                        items.append((key_to_abbr(k), str(v)))
                    items.sort(key=lambda t: t[0])
                    overrides_str = ", ".join([f"{abbr}={val}" for abbr, val in items])
                    title_label = f"Rank #{rank}, Profile {cfg_num:02d}, {config_group_str}\n$({overrides_str})$"
                else:
                    title_label = f"Rank #{rank}, Profile {cfg_num:02d}, {config_group_str}"
                log_label = f"cfg@{cfg_num} ({overrides_str if overrides else 'no overrides'})"
            else:
                title_label = f"Rank #{rank}, {run_id}"
                log_label = run_id
        except SystemExit:
            title_label = f"Rank: #{rank}, {run_id}"
            log_label = run_id
            config_group = None
        
        log.info(f"  Rank #{rank}: {run_id} | reward={reward:.2f} | label={log_label}")
        
        # Find run_dir in BASE_REPORTS_DIR
        run_dir = None
        for root, dirs, files in os.walk(BASE_REPORTS_DIR):
            for dir_name in dirs:
                if dir_name == run_id:
                    run_dir = os.path.join(root, dir_name)
                    break
            if run_dir:
                break
        
        if not run_dir:
            log.warning(f"Run directory not found in {BASE_REPORTS_DIR} for run_id '{run_id}'. Skipping.")
            continue
        
        # Auto-detect episodes if not specified
        episodes_to_use = episodes
        if not episodes_to_use:
            try:
                episodes_to_use = auto_detect_episodes(run_dir)
                log.debug(f"Auto-detected {len(episodes_to_use)} episodes for {run_id}")
            except FileNotFoundError:
                log.warning(f"Cannot auto-detect episodes for {run_id}. Skipping.")
                continue
        
        # Aggregate
        success, aggregated, status_msg = aggregate_trajectory_frequencies(run_dir, episodes_to_use)
        if not success or not aggregated:
            log.warning(f"Failed to aggregate for {run_id}: {status_msg}")
            continue
        
        # Convert to DataFrame
        df = convert_aggregated_to_dataframe(aggregated)
        if len(df) == 0:
            log.warning(f"No valid trajectory data for {run_id}. Skipping.")
            continue
        
        # Store unique trajectory count (each row in df is a unique trajectory length)
        unique_lengths = len(df)
        aggregated_dataframes.append((rank, title_label, overrides, unique_lengths, df, config_group))
    
    log.info(LINE_LENGTH * "-")
    
    if not aggregated_dataframes:
        _exit_with_warning("No valid runs found to compare.")
    
    # Generate comparison plot
    log.info(f"Generating comparison plot for {len(aggregated_dataframes)} configs")
    plot_compareall_trajectory_distribution(
        dataframes_with_labels=aggregated_dataframes,
        out_dir=out_dir,
        title=suptitle
    )


def plot_compareall_trajectory_distribution(
    dataframes_with_labels: list[tuple[int, str, dict, int, pd.DataFrame, Optional[str]]],
    out_dir: str,
    title: Optional[str] = None
) -> None:
    """Plot aggregated trajectory distributions from multiple configs for comparison.
    
    Colors are assigned based on alphabetically sorted config_groups to match bestof_plotter's behavior.
    Configs without a config_group are assigned colors after groups, in their original order.
    
    Args:
        dataframes_with_labels: List of (rank, title_label, overrides_dict, unique_lengths, dataframe, config_group) tuples
        out_dir: Output directory for comparison plot
        title: Optional custom title
    """
    if not dataframes_with_labels:
        log.warning("No dataframes to plot")
        return
    
    os.makedirs(out_dir, exist_ok=True)
    
    # Build mapping from config_group to color index
    # Sort config groups alphabetically, then assign remaining None values at the end
    config_groups = sorted(set(cg for _, _, _, _, _, cg in dataframes_with_labels if cg is not None))
    cg_to_color_idx = {cg: idx for idx, cg in enumerate(config_groups)}
    
    # For None values, assign indices after all config groups
    none_count = sum(1 for _, _, _, _, _, cg in dataframes_with_labels if cg is None)
    next_idx = len(config_groups)
    
    log.debug(f"Config groups (alphabetically sorted): {config_groups}")
    log.debug(f"Color mapping: {cg_to_color_idx}")
    log.debug(f"Number of runs without config_group: {none_count}")
    
    # Create figure with multiple subplots (one per config)
    num_configs = len(dataframes_with_labels)
    
    # Calculate grid layout (try to make it roughly square)
    cols = int(np.ceil(np.sqrt(num_configs)))
    rows = int(np.ceil(num_configs / cols))
    
    fig, axes = plt.subplots(rows, cols, figsize=(16, 4 * rows))
    
    # Flatten axes array for easier iteration
    if num_configs == 1:
        axes = [axes]
    else:
        axes = axes.flatten()
    
    final_title = title or "Aggregated Trajectory Distribution Comparison (All Configs)"
    fig.suptitle(final_title, fontweight='bold', fontsize=14, y=0.98)
    
    # Adjust figure spacing to accommodate 2-line subplot titles
    fig.subplots_adjust(top=0.95, hspace=0.35)
    
    # Generate color palette matching bestof_plotter for consistent colors across configs
    # Need enough colors for all unique config_groups + configs without group
    num_unique_colors = len(config_groups) + none_count
    palette = sns.color_palette(BESTOF_CMAP, n_colors=num_unique_colors)
    
    # Plot each config
    none_idx = 0  # Counter for None config_group indices
    for plot_idx, (rank, title_label, overrides, unique_lengths, df, config_group) in enumerate(dataframes_with_labels):
        ax = axes[plot_idx]
        
        # Determine color index based on config_group
        if config_group is not None:
            color_idx = cg_to_color_idx[config_group]
        else:
            color_idx = len(config_groups) + none_idx
            none_idx += 1
        
        if len(df) == 0:
            ax.text(0.5, 0.5, f"No data for {title_label}", ha='center', va='center',
                   transform=ax.transAxes, fontsize=10, color='red')
            ax.set_xticks([])
            ax.set_yticks([])
            continue
        
        # Calculate summary statistics
        max_len = int(df["trajectory"].max()) if len(df) > 0 else 0
        mean_len = float((df["trajectory"] * df["probability"]).sum()) if len(df) > 0 else 0
        max_p = float(df["probability"].max()) if len(df) > 0 else 0
        mode_len = int(df.loc[df["probability"] == max_p, "trajectory"].min()) if max_p > 0 else 0
        total_sum = int(df["sum_frequency"].sum()) if "sum_frequency" in df.columns else 0
        
        # Plot trajectory distribution using logarithmic X-axis
        color = palette[color_idx]
        # linestyle = LINE_STYLES[color_idx % len(LINE_STYLES)] # might be cutting off the data, so stick to regular lines
        linestyle = 'solid'
        ax.semilogx(df["trajectory"], df["probability"], linewidth=2.5, color=color,
                    linestyle=linestyle, label="Probability (PMF)", marker='o' if len(df) < 5 else '', markersize=6, alpha=0.8)
        ax.fill_between(df["trajectory"], df["probability"], alpha=0.2, color=color)
        
        # Configure logarithmic X-axis
        ax.xaxis.set_major_locator(LogLocator(base=10, numticks=10))
        ax.xaxis.set_minor_locator(LogLocator(base=10, subs=np.arange(2, 10) * 0.1))
        ax.xaxis.set_major_formatter(LogFormatterSciNotation(base=10))
        ax.set_xlabel("Step Length $l$ (log scale)", fontsize=10, fontweight='bold')
        ax.set_ylabel("Probability Density $P(l)$", fontsize=10, fontweight='bold')
        ax.set_xlim(1, max(500, df["trajectory"].max() * 1.0))
        
        # Configure Y-axis with fixed ticks from 0 to 1.0 with 0.1 step
        ax.set_yticks(np.arange(0, 1.1, 0.1))
        ax.set_ylim(0, 1.0)
        
        ax.grid(True, alpha=0.5, which='both', linestyle='--')
        ax.margins(x=0)
        
        # Set title with formatted label (includes LaTeX if present) - 2-line format with reduced height
        ax.set_title(title_label, fontsize=10, fontweight='bold', pad=0, multialignment='center')
        
        # Add legend with statistics
        from matplotlib.lines import Line2D
        handles, labels = ax.get_legend_handles_labels()
        
        # Build legend entries for statistics with programmatic fixed-width formatting
        # Using monospace font ensures proper column alignment
        stat_data = [
            ('Max trajectory', f'{max_len}'),
            ('Highest PMF', f'{max_p:.3f}'),
            ('Mean Length (PMF)', f'{mean_len:.2f}'),
            ('Most probable (mode)', f'{mode_len}'),
            ('Sum of all', f'{total_sum}'),
            ('Unique Lengths', f'{unique_lengths}'),
        ]
        
        # Find max key length for alignment
        max_key_len = max(len(key) for key, _ in stat_data)
        
        # Format entries with padding
        stat_entries = [
            Line2D([], [], linestyle='none', color='none', 
                  label=f'{key.ljust(max_key_len)} : {value}')
            for key, value in stat_data
        ]
        
        handles.extend(stat_entries)
        # Use monospace font for proper alignment of tabular data
        ax.legend(handles=handles, loc='best', fontsize=8, framealpha=0.9,
                 prop={'family': 'monospace'})
    
    # Hide unused subplots
    for idx in range(num_configs, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plot_file = os.path.join(out_dir, "Aggregated Trajectory Distribution (Compare-All).png")
    plt.savefig(plot_file, bbox_inches='tight', dpi=100)
    plt.close()
    log.info(f"Saved comparison plot: {plot_file}")


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
    
    parser.add_argument(
        "-c", "--config", type=str, required=False,
        help="Config indices to filter by (e.g. '1', '1-5', '1,3,5-7'). If not provided, all configs are processed."
    )
    
    parser.add_argument(
        "--compareall", action="store_true",
        help="Compare aggregated trajectory distributions across all configs in -pid. Requires -pid with summary.csv."
    )
    
    args = parser.parse_args()
    
    if not args.parent_id and not args.run_id:
        parser.print_help()
        sys.exit()
    
    # Parse and validate --config if provided
    config_indices: Union[list[int], None] = None
    if args.config:
        try:
            config_indices = parse_config_indices(args.config)
            log.info(f"Config filtering enabled: {args.config} → indices {config_indices}")
        except ValueError as e:
            _exit_with_warning(f"Invalid config format: {e}")
    
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
    
    # Route to compareall mode if flag is set
    if args.compareall:
        if not args.parent_id:
            _exit_with_warning("--compareall requires -pid/--parent_id to be specified")
        
        log.info("=" * LINE_LENGTH)
        log.info("COMPARE-ALL MODE: Aggregating and comparing trajectory distributions across configs")
        log.info("=" * LINE_LENGTH)
        
        run_compareall(
            parent_id=args.parent_id,
            episodes=requested_episodes if requested_episodes else None,
            suptitle=args.title,
            config_indices=config_indices
        )
        
        log.info("=" * LINE_LENGTH)
        log.info("Trajectory comparison complete")
        log.info("=" * LINE_LENGTH)
        return
    
    # Process parent_id(s) in standard mode (with optional config filtering)
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
            
            # Filter by config indices if specified
            if config_indices is not None:
                run_dirs = [
                    run_dir for run_dir in run_dirs
                    if extract_cfg_index(os.path.basename(run_dir)) in config_indices
                ]
                if not run_dirs:
                    log.warning(f"No runs found matching requested configs: {config_indices}")
                    continue
                log.info(f"Filtered to {len(run_dirs)} runs matching configs: {config_indices}")
            
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

