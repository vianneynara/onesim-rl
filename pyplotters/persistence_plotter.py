"""

"""

import os
import sys
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd
import seaborn as sns
import datetime as dt
import argparse
import matplotlib.pyplot as plt

from typing import List, Tuple, Union
from scipy.stats import gaussian_kde
from matplotlib.ticker import LogLocator, LogFormatter, LogFormatterMathtext, FormatStrFormatter

BASE_REPORTS_DIR = "reports\\skripsi"
PLOT_RESULTS_DIR = "pyplotters\\plots"

SUMMARY_KEYS = [
    "configuration_directory",
    "max_cumulative_reward",
    "max_cumulative_true_detections",
    "max_trajectory_length",
]


def log_print(msg: str, end: str = "\n"):
    print(f"[PLOTTER] {msg}", end=end)
    # print(f"[{dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", end=end)


def check_exists_source_dir(dir_path):
    if not os.path.exists(dir_path):
        raise FileNotFoundError(f"The base source directory {dir_path} does not exist.")


def read_json_file(file_path):
    json_data = None
    try:
        with open(file_path, "r") as file:
            json_data = json.load(file)
    except FileNotFoundError:
        log_print(f"The file {file_path} does not exist.")
        raise FileNotFoundError(f"The json file {file_path} does not exist.")
    return json_data


def retrieve_episode_json_dirs(_run_id_dir) -> list[str]:
    # Find all JSON files in the run_dir, where "ep" is the episode folder, having subfolders of 1, 2, 3... each ahving a JSON file
    episodes_dir = glob.glob(os.path.join(_run_id_dir, "ep", "*"))
    log_print(f"Found {len(episodes_dir)} episodes directories.")
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
            log_print(f"The key 'currentEpisodeReward' does not exist in the JSON data.")
            raise KeyError(f"The key 'currentEpisodeReward' does not exist in the JSON data.")
    return episodic_rewards


def plot_by_episode(_df: pd.DataFrame, _key: str, _title: str, _xlabel: str, _ylabel: str, file_path: str):
    plt.figure(figsize=(10, 6))

    max_episodes = _df["episodeNumber"].max()
    min_episodes = _df["episodeNumber"].min()

    sns.lineplot(data=_df, x="episodeNumber", y=_key)

    if max_episodes <= 20:
        ticks = np.arange(min_episodes, max_episodes + 1, 1)
    else:
        step = max(1, max_episodes // 10)
        start = (min_episodes // step) * step
        ticks = np.arange(start, max_episodes + 1, step)

    plt.xticks(ticks)

    # Labels & title
    plt.title(_title)
    plt.xlabel(_xlabel)
    plt.ylabel(_ylabel)

    plt.margins(x=0)
    plt.xlim(left=min_episodes)
    plt.savefig(file_path, bbox_inches='tight')
    plt.close()


def retrieve_trajectoryFrequencies(_json_data):
    traj_freq_list = []
    for trajectory_length, frequency in _json_data["trajectoryFrequencies"].items():
        traj_freq_list.append({"trajectory": trajectory_length, "frequency": frequency})

    traj_freq_df = pd.DataFrame(sorted(traj_freq_list, key=lambda x: int(x["trajectory"])))

    # Calculate probabilities
    traj_freq_df["probability"] = traj_freq_df["frequency"] / traj_freq_df["frequency"].sum()

    # Calculate PDF using Kernel Density Estimation
    trajectory_values = traj_freq_df["trajectory"].astype(int).values
    # Create weights based on frequency for KDE
    kde = gaussian_kde(trajectory_values, weights=traj_freq_df["frequency"].values, bw_method='scott')
    traj_freq_df["pdf"] = kde(trajectory_values)

    return traj_freq_df


def plot_trajectoryDistribution(_df: pd.DataFrame, file_path: str, logarithmic_x: bool = False):
    """
    Plots both the probability mass function and probability density function of trajectories.
    - Blue line: Raw probabilities (PMF)
    - Orange line: Smoothed PDF (KDE)
    """
    plt.figure(figsize=(12, 6))

    if not logarithmic_x:
        # Plot both probability and PDF
        sns.lineplot(data=_df, x="trajectory", y="probability", label="Probability (PMF)", linewidth=2)
        sns.lineplot(data=_df, x="trajectory", y="pdf", label="Probability Density (KDE)", linewidth=2, linestyle="--")

        plt.title("Trajectory Distribution: PMF vs PDF")
        plt.xlabel("Trajectory Length")
        plt.ylabel("Probability / Density")
        plt.gca().set_yticks(np.arange(0, 1.1, 0.1))
        plt.margins(x=0)
        plt.legend()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()
    else:
        # Logarithmic X-axis
        sns.lineplot(data=_df, x="trajectory", y="probability", label="Probability (PMF)", linewidth=2)
        sns.lineplot(data=_df, x="trajectory", y="pdf", label="Probability Density (KDE)", linewidth=2, linestyle="--")

        plt.title("Trajectory Distribution: PMF vs PDF (Logarithmic Scale)")
        plt.xlabel("Trajectory Length (log scale)")
        plt.ylabel("Probability / Density")

        # Set X-axis to logarithmic scale with dynamic range
        ax = plt.gca()
        ax.set_xscale('log')

        # Determine X-axis limits based on max trajectory value
        max_trajectory = float(_df["trajectory"].max())
        x_min = 10 ** 0  # Always start from 10^0

        if max_trajectory < 10 ** 2:
            x_max = 10 ** 2  # At least show up to 10^2
        elif max_trajectory < 10 ** 3:
            x_max = 10 ** 3  # If data reaches 10^2, show up to 10^3
        else:
            x_max = 10 ** 4  # If data exceeds 10^3, show up to 10^4

        ax.set_xlim(x_min, x_max)
        ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=10))
        ax.xaxis.set_major_formatter(LogFormatterMathtext(base=10.0))

        # Y-axis ticks at 0.1 intervals
        ax.set_yticks(np.arange(0, 1.1, 0.1))

        plt.margins(x=0)
        plt.legend()
        plt.savefig(file_path, bbox_inches='tight')
        plt.close()


def process_reports(_run_id_dir):
    """
    Common DF includes:
    episodeNumber, currentEpisodeReward, currentCumulativeReward, previousCumulativeRewards, currentTrueDetections,
    currentCumulativeTrueDetections, previousCumulativeTrueDetections

    """
    episode_jsons_dir = retrieve_episode_json_dirs(_run_id_dir)

    _run_summary = {key:float("-inf") for key in SUMMARY_KEYS}
    _run_summary["configuration_directory"] = _run_id_dir.split("\\")[-1]

    COMMON_IDX = ["episodeNumber", "currentEpisodeReward", "currentCumulativeReward", "previousCumulativeReward",
                  "currentTrueDetections", "currentCumulativeTrueDetections", "previousCumulativeTrueDetections"]
    common_df = pd.DataFrame(columns=COMMON_IDX)

    # Use the last episodic JSON file to determine the number of trajectories
    traj_freq_df = retrieve_trajectoryFrequencies(read_json_file(episode_jsons_dir[-1]))

    for episode_json_dir in episode_jsons_dir:
        log_print(f"Processing JSON file: {episode_json_dir}")
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
    pp_currentEpisodeReward = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"currentEpisodeReward.png")
    plot_by_episode(
        common_df,
        "currentEpisodeReward",
        "Current Episode Reward",
        "Episode",
        "Reward",
        pp_currentEpisodeReward
    )

    # currentTrueDetections
    pp_currentTrueDetections = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"currentTrueDetections.png")
    plot_by_episode(
        common_df,
        "currentTrueDetections",
        "Current True Detections",
        "Episode",
        "Detection",
        pp_currentTrueDetections
    )

    # trajectory distribution
    plot_trajectoryDistribution(
        traj_freq_df,
        os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"trajectoryDistribution.png")
    )
    plot_trajectoryDistribution(
        traj_freq_df,
        os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"trajectoryDistributionLog.png"),
        logarithmic_x=True
    )

    return _run_summary


if __name__ == "__main__":
    check_exists_source_dir(BASE_REPORTS_DIR)

    parser = argparse.ArgumentParser(
        description="ONE Simulator persistence files plotter. Converts JSON persistence into graphs."
    )

    parser.add_argument(
        "-ao", "--all_of", type=str, help="The parent report source directory. (e.g. \"ql\")"
    )

    parser.add_argument(
        "-ri", "--run_id", type=str, help="The parent report source directory. (e.g. \"ql\")"
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
            log_print(f"No run-id directories found under {all_of_dir}. Checking for direct subdirectories instead.")
            run_dirs = glob.glob(os.path.join(all_of_dir, "*"))

        for run_dir in run_dirs:
            if os.path.isdir(run_dir):
                log_print(f"Processing result directory: {run_dir}")
                run_summary = process_reports(run_dir)

                summary_df = pd.concat([summary_df, pd.DataFrame([run_summary])], ignore_index=True)

        log_print("Done processing all results.")
        os.makedirs(os.path.join(PLOT_RESULTS_DIR, args.all_of), exist_ok=True)
        log_print("Saving summary to CSV file: " + os.path.join(PLOT_RESULTS_DIR, args.all_of, "summary.csv"))
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
            log_print(f"The run-id {args.run_id} does not exist.")
            raise FileNotFoundError(f"The run-id {args.run_id} does not exist under {BASE_REPORTS_DIR}.")

        check_exists_source_dir(run_dir)
        log_print(f"Processing result directory: {run_dir}")

        process_reports(run_dir)
