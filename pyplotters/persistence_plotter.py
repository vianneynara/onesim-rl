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

log = logging.getLogger(__name__)

PARENT_DIR       = "mcn1"
BASE_REPORTS_DIR = "reports\\skripsi"
PLOT_RESULTS_DIR = f"pyplotters\\plots\\{PARENT_DIR}"

SUMMARY_KEYS = [
    "configuration_directory",
    "max_cumulative_reward",
    "max_cumulative_true_detections",
    "max_trajectory_length",
]

def check_exists_source_dir(dir_path):
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The base source directory {dir_path} does not exist.")


def read_json_file(file_path):
    json_data = None
    try:
        with open(file_path, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        log.info(f"The file {file_path} does not exist.")
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


def plot_by_episode(_df: pd.DataFrame, _key: str, _title: str, _xlabel: str, _ylabel: str, file_path: str, _yalias: str = None, _discrete: bool = False):
    plt.figure(figsize=(10, 6))

    if not _yalias:
        _yalias = _ylabel

    max_episodes = _df["episodeNumber"].max()
    min_episodes = _df["episodeNumber"].min()

    sns.lineplot(data=_df, x="episodeNumber", y=_key)

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
    plt.title(_title, fontweight='bold')
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


def plot_trajectoryDistribution(_df: pd.DataFrame, file_path: str, logarithmic_x: bool = False):
    """
    Plots both the probability mass function and probability density function of trajectories.
    - Blue line: Raw probabilities (PMF)
    - Orange line: Smoothed PDF (KDE)
    """
    plt.figure(figsize=(12, 6))
    xmax_plot = 50

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

    if not logarithmic_x:
        # Plot both probability and PDF
        sns.lineplot(data=_df, x="trajectory", y="probability", label="Probability (PMF)", linewidth=2)

        plt.title("Trajectory Distribution (Probability Mass Function)")
        plt.xlabel("Trajectory Length")
        plt.ylabel("Probability / Density")

        ax = plt.gca()
        ax.set_xlim(1, xmax_plot)

        # Major tick every 200; minor tick every 50 (optional)
        ax.xaxis.set_major_locator(MultipleLocator(10))
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
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
    else:
        # Logarithmic X-axis
        sns.lineplot(data=_df, x="trajectory", y="probability", label="Probability (PMF)", linewidth=2)

        plt.title("Trajectory Distribution (Probability Mass Function)")
        plt.xlabel("Trajectory Length (log scale)")
        plt.ylabel("Probability / Density")

        # Set X-axis to logarithmic scale with dynamic range
        ax = plt.gca()
        ax.set_xscale('log')

        # Set X-axis ticks from 10^0 to 10^3
        # xmax_plot = _df["trajectory"].max()
        ax.set_xlim(1, xmax_plot)
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
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()


def process_reports(_run_id_dir):
    """
    Common DF includes:
    episodeNumber, currentEpisodeReward, currentCumulativeReward, previousCumulativeRewards, currentTrueDetections,
    currentUniqueDetections, currentCumulativeTrueDetections, previousCumulativeTrueDetections

    """
    episode_jsons_dir = retrieve_episode_json_dirs(_run_id_dir)

    _run_summary = {key:float("-inf") for key in SUMMARY_KEYS}
    _run_summary["configuration_directory"] = _run_id_dir.split("\\")[-1]

    COMMON_IDX = ["episodeNumber", "currentEpisodeReward", "currentCumulativeReward", "previousCumulativeReward",
                  "currentTrueDetections", "currentUniqueDetections", "currentCumulativeTrueDetections",
                  "previousCumulativeTrueDetections"]
    common_df = pd.DataFrame(columns=COMMON_IDX)

    # Use the last episodic JSON file to determine the number of trajectories
    traj_freq_df = retrieve_trajectoryFrequencies(read_json_file(episode_jsons_dir[-1]))

    for episode_json_dir in episode_jsons_dir:
        log.info(f"Processing JSON file: {episode_json_dir}")
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

    common_df_path = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"common_data.csv")

    # make sure path exists
    os.makedirs(os.path.dirname(common_df_path), exist_ok=True)

    common_df.to_csv(common_df_path, index=False, sep=";", header=True)

    # currentEpisodeReward
    pp_currentEpisodeReward = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"Current Episode Reward.png")
    plot_by_episode(
        common_df,
        "currentEpisodeReward",
        "Current Episode Reward",
        "Episode",
        "Reward",
        pp_currentEpisodeReward,
        _yalias="reward"
    )

    # currentEpisodeReward
    pp_currentCumulativeReward = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"Current Cumulative Reward.png")
    plot_by_episode(
        common_df,
        "currentCumulativeReward",
        "Current Cumulative Reward",
        "Episode",
        "Reward",
        pp_currentCumulativeReward,
        _yalias="cumu. reward"
    )

    # currentTrueDetections
    pp_currentTrueDetections = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"Current True Detections.png")
    plot_by_episode(
        common_df,
        "currentTrueDetections",
        "Current True Detections",
        "Episode",
        "Detection",
        pp_currentTrueDetections,
        _yalias="detection",
        _discrete=True
    )

    # currentUniqueDetections
    pp_currentUniqueDetections = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"Current Unique Detections.png")
    plot_by_episode(
        common_df,
        "currentUniqueDetections",
        "Current Unique Detections",
        "Episode",
        "Detection",
        pp_currentUniqueDetections,
        _yalias="uniq. detection",
        _discrete=True
    )

    # trajectory distribution
    plot_trajectoryDistribution(
        traj_freq_df,
        os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"Trajectory Distribution.png")
    )
    plot_trajectoryDistribution(
        traj_freq_df,
        os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"Trajectory Distribution (log scale).png"),
        logarithmic_x=True
    )

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

        for run_dir in run_dirs:
            if os.path.isdir(run_dir):
                log.info(f"Processing result directory: {run_dir}")
                run_summary = process_reports(run_dir)

                summary_df = pd.concat([summary_df, pd.DataFrame([run_summary])], ignore_index=True)

        log.info("Done processing all results.")
        os.makedirs(os.path.join(PLOT_RESULTS_DIR, args.all_of), exist_ok=True)
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

        process_reports(run_dir)
