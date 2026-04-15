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
from matplotlib.ticker import LogLocator, LogFormatter, LogFormatterMathtext, FormatStrFormatter

BASE_REPORTS_DIR = "reports\\skripsi"
PLOT_RESULTS_DIR = "pyplotters\\plots"


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


def process_reports(_run_id_dir):
    """
    Common DF includes:
    episodeNumber, currentEpisodeReward, currentCumulativeReward, previousCumulativeRewards, currentTrueDetections, currentCumulativeTrueDetections, previousCumulativeTrueDetections


    """
    episode_jsons_dir = retrieve_episode_json_dirs(_run_id_dir)

    COMMON_IDX = ["episodeNumber", "currentEpisodeReward", "currentCumulativeReward", "previousCumulativeReward", "currentTrueDetections", "currentCumulativeTrueDetections", "previousCumulativeTrueDetections"]
    common_df = pd.DataFrame(columns=COMMON_IDX)

    for episode_json_dir in episode_jsons_dir:
        log_print(f"Processing JSON file: {episode_json_dir}")
        json_data = read_json_file(episode_json_dir)

        # Collect all values for this episode
        row_data = {key: json_data[key] for key in COMMON_IDX}

        # Add the complete row to the dataframe
        common_df = pd.concat([common_df, pd.DataFrame([row_data])], ignore_index=True)

        # episodic_rewards = sequence_of_currentEpisodeReward(json_data)
        #
        # # Creating the plot, X axis is the episode number, Y axis is the episodic reward
        # plt.plot(episodic_rewards)
        # plt.xlabel("Episode")
        # plt.ylabel("Episodic Reward")
        # plt.title(f"Episodic Reward for Episode {episode_json_dir.split('/')[-2]}")
        # plt.savefig(os.path.join(PLOT_RESULTS_DIR, f"episodic_reward_{episode_json_dir.split('/')[-2]}.png"))
        # plt.show()

    common_df_path = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"common_data.csv")

    # make sure path exists
    os.makedirs(os.path.dirname(common_df_path), exist_ok=True)

    common_df.to_csv(common_df_path, index=False, sep=";", header=True)

    pp_currentEpisodeReward = os.path.join(PLOT_RESULTS_DIR, _run_id_dir.split("\\")[-1], f"currentEpisodeReward.png")
    plot_by_episode(
        common_df,
        "currentEpisodeReward",
        "Current Episode Reward",
        "Episode",
        "Reward",
        pp_currentEpisodeReward
    )


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

        run_dirs = glob.glob(os.path.join(all_of_dir, "run-id", "*"))
        for run_dir in run_dirs:
            if os.path.isdir(run_dir):
                log_print(f"Processing result directory: {run_dir}")
                process_reports(run_dir)

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
