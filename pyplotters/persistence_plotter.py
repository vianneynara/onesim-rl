"""

"""

import os
import sys
import glob
import json
import logging
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
import argparse
import matplotlib.pyplot as plt

from typing import List, Tuple, Union
from scipy.stats import gaussian_kde
from matplotlib.ticker import LogLocator, LogFormatter, LogFormatterMathtext, FormatStrFormatter, MultipleLocator

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

LIST_OF_IGNORED_OVERRIDES = [
    "cfg",  # config index
    "cg",   # config group
    "ql500",  # Q-Learning with 500 runs
    "lfe500"  # Lévy Flight with 500 runs
]

SUMMARY_KEYS = [
    "configuration_directory",
    "max_cumulative_reward",
    "last_episode_cumulative_reward",
    "mean_cumulative_reward",
    "max_cumulative_true_detections",
    "max_trajectory_length",
]

def check_exists_source_dir(dir_path):
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The base source directory {dir_path} does not exist.")


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


def read_json_file(file_path):
    json_data = None
    try:
        with open(file_path, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        log.error(f"The file {file_path} does not exist.")
        raise FileNotFoundError(f"The json file {file_path} does not exist.")
    return json_data


def retrieve_episode_json_dirs(_run_id_dir) -> list[str]:
    # Find all JSON files in the run_dir, where "ep" is the episode folder, having subfolders of 1, 2, 3... each ahving a JSON file
    episodes_dir = glob.glob(os.path.join(_run_id_dir, "ep", "*"))
    log.info(f"Found {len(episodes_dir)} episodes directories.")
    episode_jsons_dir = []

    for episode_dir in episodes_dir:
        episode_json_dir = glob.glob(os.path.join(episode_dir, "*.json"))
        episode_jsons_dir.extend(episode_json_dir)

    return episode_jsons_dir


def sequence_of_currentEpisodeReward(json_data) -> list[int]:
    # Retrieve the sequence of currentEpisodeReward from the JSON data
    episodic_rewards = []
    for entry in json_data:
        if "currentEpisodeReward" in entry:
            episodic_rewards.append(entry["currentEpisodeReward"])
        else:
            log.info(f"The key 'currentEpisodeReward' does not exist in the JSON data.")
            raise KeyError(f"The key 'currentEpisodeReward' does not exist in the JSON data.")
    return episodic_rewards


def plot_by_episode(_df: pd.DataFrame, _key: str, _title: str, _xlabel: str, _ylabel: str, file_path: str, _yalias: str = None, _discrete: bool = False, _ema_line: bool = False, _ma_line: bool = False, _subtitle: str = None, _description: str = None):
    plt.figure(figsize=(10, 6))

    if not _yalias:
        _yalias = _ylabel


    max_episodes = _df["episodeNumber"].max()
    min_episodes = _df["episodeNumber"].min()

    sns.lineplot(data=_df, x="episodeNumber", y=_key, label=_yalias, color="skyblue")

    if _ema_line:
        _ema_series = pd.Series(_df[_key]).ewm(span=20, adjust=False).mean()
        sns.lineplot(data=_df, x="episodeNumber", y=_ema_series, label="EMA", color="orange")

    if _ma_line:
        _ma_series = pd.Series(_df[_key]).rolling(window=20).mean()
        sns.lineplot(data=_df, x="episodeNumber", y=_ma_series, label="MA", color="green")

    # Summary statistics for the selected Y series
    y = pd.to_numeric(_df[_key], errors="coerce")
    y = y.dropna()
    y_max = y_min = y_mean = y_mode = None
    if len(y) > 0:
        y_max = float(y.max())
        y_min = float(y.min())
        y_mean = float(y.mean())
        # Pandas mode can return multiple values; pick the first (smallest)
        modes = y.mode()
        y_mode = float(modes.iloc[0]) if len(modes) > 0 else None

    if max_episodes <= 20:
        ticks = np.arange(min_episodes, max_episodes + 1, 1)
    else:
        step = max(1, max_episodes // 10)
        start = (min_episodes // step) * step
        ticks = np.arange(start, max_episodes + 1, step)

    plt.xticks(ticks)

    # Labels & title
    # Construct title with main title and optional subtitle
    title_lines = []
    if _title:
        title_lines.append(_title)
    if _subtitle:
        title_lines.append(_subtitle)
    
    main_title = "\n".join(title_lines) if title_lines else ""
    
    # Add main title as suptitle (above plot area)
    fig = plt.gcf()
    fig.suptitle(main_title, fontweight='bold', fontsize=12, y=0.98)
    
    # Add description as lighter text if present
    if _description:
        fig.text(0.5, 0.91, _description, ha='center', va='top', 
                fontsize=9, fontweight='light', style='italic', color='gray')
        # Adjust top margin to accommodate both title and description
        fig.subplots_adjust(top=0.88)
    else:
        # Adjust top margin for title only
        fig.subplots_adjust(top=0.92)
    
    plt.xlabel(_xlabel)
    plt.ylabel(_ylabel)

    plt.margins(x=0)
    plt.xlim(left=min_episodes)

    # Add summary stats into legend without adding visual lines to the plot.
    ax = plt.gca()
    handles, labels = ax.get_legend_handles_labels()
    if y_max is not None:
        from matplotlib.lines import Line2D

        # Use monospace to keep alignment stable
        if not _discrete:
            stat_lines = [
                f"{'Highest ' + _yalias:<20}: {y_max:>10.4f}",
                f"{'Lowest ' + _yalias:<20}: {y_min:>10.4f}",
                f"{'Mean ' + _yalias:<20}: {y_mean:>10.4f}",
            ]
        else:
            y_max = int(y_max)
            y_min = int(y_min)
            stat_lines = [
                f"{'Highest ' + _yalias:<20}: {y_max:>10d}",
                f"{'Lowest ' + _yalias:<20}: {y_min:>10d}",
                f"{'Mean ' + _yalias:<20}: {y_mean:>10.2f}",
            ]
        # if y_mode is not None:
        #     stat_lines.append(f"{'Mode ' + _yalias:<24}: {y_mode:>12.4f}")

        handles.extend([Line2D([], [], linestyle='none', color='none', label=s) for s in stat_lines])

    if handles:
        ax.legend(handles=handles, loc="best", prop={'family': 'monospace'})

    # Ensure output directory exists (savefig does not create directories)
    out_dir = os.path.dirname(file_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    plt.savefig(file_path, bbox_inches='tight')
    plt.close()


def retrieve_trajectoryFrequencies(_json_data):
    traj_freq_list = []
    for trajectory_length, frequency in _json_data["trajectoryFrequencies"].items():
        traj_freq_list.append({"trajectory": trajectory_length, "frequency": frequency})

    traj_freq_df = pd.DataFrame(sorted(traj_freq_list, key=lambda x: int(x["trajectory"])))

    # Calculate probabilities
    traj_freq_df["probability"] = traj_freq_df["frequency"] / traj_freq_df["frequency"].sum()

    # Calculate PDF (Probability Mass Function) using Kernel Density Estimation
    trajectory_values = traj_freq_df["trajectory"].astype(int).values

    return traj_freq_df


def plot_trajectoryDistribution(
        _df: pd.DataFrame,
        file_path: str,
        logarithmic_x: bool = False,
        x_max: int = 500,
        _title: str = None,
        _subtitle: str = None,
        _description: str = None
):
    """
    Plots both the probability mass function and probability density function of trajectories.
    - Blue line: Raw probabilities (PMF)
    - Orange line: Smoothed PDF (KDE)
    """
    plt.figure(figsize=(12, 6))

    # Ensure numeric dtypes (JSON keys often arrive as strings)
    _df = _df.copy()
    _df["trajectory"] = _df["trajectory"].astype(int)
    _df["probability"] = _df["probability"].astype(float)

    # Summary statistics to display in legend
    max_len = None
    mean_len = None
    max_p = None
    mode_len = None
    if len(_df) > 0 and float(_df["probability"].sum()) > 0:
        max_len = int(_df["trajectory"].max())
        # Expected trajectory length under PMF
        mean_len = float((_df["trajectory"] * _df["probability"]).sum())
        # Most probable trajectory length (mode); in ties pick the smallest length
        max_p = _df["probability"].max()
        mode_len = int(_df.loc[_df["probability"] == max_p, "trajectory"].min())

    suptitle_y = 0.98
    if not logarithmic_x:
        # Plot both probability and PDF
        sns.lineplot(data=_df, x="trajectory", y="probability", label="Probability (PMF)", linewidth=2)

        # Construct multi-line title
        title_parts = [_title or "Trajectory Distribution (Probability Mass Function)"]
        if _subtitle:
            title_parts.append(_subtitle)
        else:
            suptitle_y -= 0.03
        
        final_title = "\n".join(title_parts)
        
        # Add main title as suptitle (above plot area)
        fig = plt.gcf()
        fig.suptitle(final_title, fontweight='bold', fontsize=12, y=suptitle_y)
        
        # Add description as lighter text if present
        if _description:
            fig.text(0.5, 0.91, _description, ha='center', va='top', 
                    fontsize=9, fontweight='light', style='italic', color='gray')
            fig.subplots_adjust(top=0.88)
        else:
            fig.subplots_adjust(top=0.92)
        
        ax = plt.gca()
        plt.xlabel("Trajectory Length")
        plt.ylabel("Probability / Density")
        ax.set_xlim(1, x_max)

        # Major tick every 200; minor tick every 50 (optional)
        ax.xaxis.set_major_locator(MultipleLocator(50))
        ax.xaxis.set_minor_locator(MultipleLocator(50))

        plt.gca().set_yticks(np.arange(0, 1.1, 0.1))
        plt.margins(x=0)

        # Add summary stats into legend without adding visual lines to the plot.
        # To keep the column alignment, render legend text using a monospace font.
        handles, labels = ax.get_legend_handles_labels()
        if max_len is not None:
            from matplotlib.lines import Line2D
            stat_lines = [
                f"{'Max trajectory':<20}: {max_len:>6d}",
                f"{'Highest PMF':<20}: {max_p:>10.3f}",
                f"{'Mean length (PMF)':<20}: {mean_len:>10.2f}",
                f"{'Most probable (mode)':<20}: {mode_len:>6d}",
            ]
            handles.extend([Line2D([], [], linestyle='none', color='none', label=s) for s in stat_lines])
        ax.legend(handles=handles, loc="best", prop={'family': 'monospace'})

        out_dir = os.path.dirname(file_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
    else:
        # Logarithmic X-axis
        sns.lineplot(data=_df, x="trajectory", y="probability", label="Probability (PMF)", linewidth=2)

        # Construct multi-line title
        title_parts = [_title or "Logarithmic Trajectory Distribution (Probability Mass Function)"]
        if _subtitle:
            title_parts.append(_subtitle)
        else:
            suptitle_y -= 0.03
        
        final_title = "\n".join(title_parts)
        
        # Add main title as suptitle (above plot area)
        fig = plt.gcf()
        fig.suptitle(final_title, fontweight='bold', fontsize=12, y=suptitle_y)
        
        # Add description as lighter text if present
        if _description:
            fig.text(0.5, 0.91, _description, ha='center', va='top', 
                    fontsize=9, fontweight='light', style='italic', color='gray')
            fig.subplots_adjust(top=0.88)
        else:
            fig.subplots_adjust(top=0.92)
        
        ax = plt.gca()
        plt.xlabel("Trajectory Length (log scale)")
        plt.ylabel("Probability / Density")

        # Set X-axis to logarithmic scale with dynamic range
        ax.set_xscale('log')

        # Set X-axis ticks from 10^0 to 10^3
        # xmax_plot = _df["trajectory"].max()
        ax.set_xlim(1, x_max)
        ax.set_xticks([1, 10, 100, 1000])

        # Y-axis ticks at 0.1 intervals
        ax.set_yticks(np.arange(0, 1.1, 0.1))

        plt.margins(x=0)

        handles, labels = ax.get_legend_handles_labels()
        if max_len is not None:
            from matplotlib.lines import Line2D
            stat_lines = [
                f"{'Max trajectory':<20}: {max_len:>10d}",
                f"{'Highest PMF':<20}: {max_p:>10.6f}",
                f"{'Mean length (PMF)':<20}: {mean_len:>10.2f}",
                f"{'Most probable (mode)':<20}: {mode_len:>10d}",
            ]
            handles.extend([Line2D([], [], linestyle='none', color='none', label=s) for s in stat_lines])
        ax.legend(handles=handles, loc="best", prop={'family': 'monospace'})

        out_dir = os.path.dirname(file_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        plt.savefig(file_path, bbox_inches='tight')
        plt.close()


def process_reports(_run_id_dir, _parent_dir: str = None, _title: str = None, _describe: bool = False):
    """
    Common DF includes:
    episodeNumber, currentEpisodeReward, currentCumulativeReward, previousCumulativeRewards, currentTrueDetections,
    currentUniqueDetections, currentCumulativeTrueDetections, previousCumulativeTrueDetections

    """
    episode_jsons_dir = retrieve_episode_json_dirs(_run_id_dir)
    run_id = _run_id_dir.split("\\")[-1]

    log.info(LINE_LENGTH * "-")
    log.info(f"Processing run directory: {run_id}")

    _run_summary = {key:float("-inf") for key in SUMMARY_KEYS}
    _run_summary["configuration_directory"] = _run_id_dir.split("\\")[-1]

    COMMON_IDX = ["episodeNumber", "currentEpisodeReward", "currentCumulativeReward", "previousCumulativeReward",
                  "currentTrueDetections", "currentUniqueDetections", "currentCumulativeTrueDetections",
                  "previousCumulativeTrueDetections"]
    # ADDITIONAL COLUMN: meanCumulativeReward
    common_df = pd.DataFrame(columns=COMMON_IDX)

    # Use the last episodic JSON file to determine the number of trajectories
    traj_freq_df = retrieve_trajectoryFrequencies(read_json_file(episode_jsons_dir[-1]))

    for episode_json_dir in episode_jsons_dir:
        # log.info(f"Processing JSON file: {episode_json_dir}")
        json_data = read_json_file(episode_json_dir)

        # Collect all values for this episode
        row_data = {key: json_data[key] for key in COMMON_IDX}

        # Add the complete row to the dataframe
        common_df = pd.concat([common_df, pd.DataFrame([row_data])], ignore_index=True)

        # Update summary values
        _run_summary["max_cumulative_reward"] = max(_run_summary["max_cumulative_reward"], json_data["currentCumulativeReward"])
        _run_summary["max_cumulative_true_detections"] = max(_run_summary["max_cumulative_true_detections"], json_data["currentCumulativeTrueDetections"])

        # Get highest "trajectoryFrequencies" by grabbing and selecting the highest int-casted
        _run_summary["max_trajectory_length"] = max(_run_summary["max_trajectory_length"], max([int(k) for k in json_data["trajectoryFrequencies"].keys()]))

    # SORT common_df by episodeNumber, this wsa critical bruh.
    common_df = common_df.sort_values(by=["episodeNumber"], ascending=True)

    # Adds a meanCumulativeReward column with expanded mean from currentCumulativeReward
    common_df["meanCumulativeReward"] = common_df["currentCumulativeReward"].expanding().mean()

    # Calculate mean cumulative reward after all episodes are processed
    _run_summary["mean_cumulative_reward"] = common_df["currentCumulativeReward"].mean()
    
    # Calculate last episode's cumulative reward (final performance)
    _run_summary["last_episode_cumulative_reward"] = common_df["currentCumulativeReward"].iloc[-1]

    # Output directory: pyplotters/plots[/<parent>]/<run_id>/
    _parent_results_dir = os.path.join(PLOT_RESULTS_DIR, _parent_dir) if _parent_dir else PLOT_RESULTS_DIR
    run_out_dir = os.path.join(_parent_results_dir, run_id)
    os.makedirs(run_out_dir, exist_ok=True)

    common_df_path = os.path.join(run_out_dir, "common_data.csv")
    common_df.to_csv(common_df_path, index=False, sep=";", header=True)

    # Generate description if --describe flag is set
    _description = parse_run_description(run_id) if _describe else None

    # currentEpisodeReward
    pp_currentEpisodeReward = os.path.join(run_out_dir, "Current Episode Reward.png")
    plot_by_episode(
        common_df,
        "currentEpisodeReward",
        _title,
        "Episode",
        "Reward",
        pp_currentEpisodeReward,
        _subtitle="Current Episode Reward",
        _yalias="Reward",
        _description=_description,
        # _ema_line=True,
        # _ma_line=True
    )

    # currentCumulativeReward
    pp_currentCumulativeReward = os.path.join(run_out_dir, "Current Cumulative Reward.png")
    plot_by_episode(
        common_df,
        "currentCumulativeReward",
        _title,
        "Episode",
        "Reward",
        pp_currentCumulativeReward,
        _subtitle="Current Cumulative Reward",
        _yalias="Cumu. Reward",
        _description=_description,
        # _ema_line=True,
        # _ma_line=True
    )

    # Mean Cumulative Reward (cumulative mean across episodes)
    common_df_with_mean = common_df.copy()
    common_df_with_mean["meanCumulativeReward"] = common_df_with_mean["currentCumulativeReward"].expanding().mean()
    pp_meanCumulativeReward = os.path.join(run_out_dir, "Mean Cumulative Reward.png")
    plot_by_episode(
        common_df_with_mean,
        "meanCumulativeReward",
        _title,
        "Episode",
        "Reward",
        pp_meanCumulativeReward,
        _subtitle="Mean Cumulative Reward (across episodes)",
        _yalias="Mean Cumu. Reward",
        _description=_description,
        # _ema_line=True,
        # _ma_line=True
    )

    # currentTrueDetections
    pp_currentTrueDetections = os.path.join(run_out_dir, "Current True Detections.png")
    plot_by_episode(
        common_df,
        "currentTrueDetections",
        _title,
        "Episode",
        "Detection",
        pp_currentTrueDetections,
        _subtitle="Current True Detections",
        _yalias="Detection",
        _discrete=True,
        _description=_description,
        # _ema_line=True,
        # _ma_line=True
    )

    # currentUniqueDetections
    pp_currentUniqueDetections = os.path.join(run_out_dir, "Current Unique Detections.png")
    plot_by_episode(
        common_df,
        "currentUniqueDetections",
        _title,
        "Episode",
        "Detection",
        pp_currentUniqueDetections,
        _subtitle="Current Unique Detections",
        _yalias="Uniq. Detection",
        _discrete=True,
        _description=_description,
        # _ema_line=True,
        # _ma_line=True
    )

    # trajectory distribution
    plot_trajectoryDistribution(
        traj_freq_df,
        os.path.join(run_out_dir, "Trajectory Distribution.png"),
        x_max=100,
        _title=_title,
        _subtitle="Trajectory Distribution (Probability Mass Function)",
        _description=_description
    )
    plot_trajectoryDistribution(
        traj_freq_df,
        os.path.join(run_out_dir, "Trajectory Distribution (log scale).png"),
        logarithmic_x=True,
        _title=_title,
        _subtitle="Logarithmic Trajectory Distribution (Probability Mass Function)",
        _description=_description
    )

    log.info(f"Finished processing run directory: {run_id}")
    log.info(f"Saving common data to CSV file: {common_df_path}")
    log.info(LINE_LENGTH * "=")

    return _run_summary


if __name__ == "__main__":
    check_exists_source_dir(BASE_REPORTS_DIR)

    parser = argparse.ArgumentParser(
        description="ONE Simulator persistence files plotter. Converts JSON persistence into graphs."
    )

    parser.add_argument(
        "-aof", "--all_of", type=str, help="The parent report source directory. (e.g. \"ql\")"
    )

    parser.add_argument(
        "-rid", "--run_id", type=str, help="The parent report source directory. (e.g. \"ql\")"
    )

    parser.add_argument(
        "-t", "--title", type=str, help="Custom title for plots"
    )

    parser.add_argument(
        "-d", "--describe", action="store_true", help="Parse run_id and add description to plots"
    )

    args = parser.parse_args()

    if not args.all_of and not args.run_id:
        parser.print_help()
        sys.exit()

    # Delegate to loopers to retrieve all episodic JSON data
    if args.all_of:
        all_of_dir = os.path.join(BASE_REPORTS_DIR, args.all_of)
        check_exists_source_dir(all_of_dir)
        summary_df = pd.DataFrame(columns=SUMMARY_KEYS)

        run_dirs = glob.glob(os.path.join(all_of_dir, "run-id", "*"))
        if not run_dirs:
            log.error(f"No run-id directories found under {all_of_dir}. Checking for direct subdirectories instead.")
            run_dirs = glob.glob(os.path.join(all_of_dir, "*"))

        log.info("Making sure the results directory exists: " + PLOT_RESULTS_DIR + f"/{args.all_of}/")
        os.makedirs(os.path.join(PLOT_RESULTS_DIR, args.all_of), exist_ok=True)

        for run_dir in run_dirs:
            if os.path.isdir(run_dir):
                log.info(f"Processing result directory: {run_dir}")
                run_summary = process_reports(run_dir, args.all_of, args.title, args.describe)

                summary_df = pd.concat([summary_df, pd.DataFrame([run_summary])], ignore_index=True)

        log.info("Done processing all results.")
        log.info("Saving summary to CSV file: " + os.path.join(PLOT_RESULTS_DIR, args.all_of, "summary.csv"))
        summary_df.to_csv(os.path.join(PLOT_RESULTS_DIR, args.all_of, "summary.csv"), index=False, sep=";", header=True)

    elif args.run_id:
        # Finds the args.run_id directory under BASE_REPORTS_DIR and store it in run_dir if found
        run_dir = None

        for root, dirs, files in os.walk(BASE_REPORTS_DIR):
            for dir_name in dirs:
                if dir_name == args.run_id:
                    run_dir = os.path.join(root, dir_name)
                    break

        if not run_dir:
            log.error(f"The run-id {args.run_id} does not exist.")
            raise FileNotFoundError(f"The run-id {args.run_id} does not exist under {BASE_REPORTS_DIR}.")

        check_exists_source_dir(run_dir)
        log.info(f"Processing result directory: {run_dir}")

        process_reports(run_dir, None, args.title, args.describe)
