import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# =========================
# STYLE CONFIG
# =========================
plt.style.use('seaborn-v0_8-muted')
sns.set_context("notebook", font_scale=1.2)

BASE_FOLDER = "D-MC-THS-FV-1"
QTABLE_DIR = f"data/qtable/{BASE_FOLDER}"
REPORT_DIR = f"reports/{BASE_FOLDER}"
PLOT_DIR = f"data/plotter/{BASE_FOLDER}"

os.makedirs(PLOT_DIR, exist_ok=True)

def save_plot(filename):
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, filename)
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved → {path}")

# =========================
# 1. TOTAL REWARD
# =========================
def plot_total_reward():
    episode_map = {}
    if not os.path.exists(QTABLE_DIR): return

    for file in os.listdir(QTABLE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(QTABLE_DIR, file), "r") as f:
                data = json.load(f)
            episode_map[int(data.get("episode", 0))] = data.get("totalReward", 0)

    if not episode_map: return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Reward']).sort_values('Episode')
    df['Rolling_Avg'] = df['Reward'].rolling(window=min(len(df), 10), min_periods=1).mean()

    plt.figure(figsize=(12, 6))
    plt.plot(df['Episode'], df['Reward'], alpha=0.3, label='Raw Reward')
    plt.plot(df['Episode'], df['Rolling_Avg'], linewidth=2.5, label='Trend (SMA 10)')

    plt.title("Agent Learning Progress: Total Reward")
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    save_plot("total_reward_refined.png")

# =========================
# 1B. EPISODE REWARD (NEW)
# =========================
def plot_episode_reward():
    episode_map = {}
    if not os.path.exists(QTABLE_DIR): return

    for file in os.listdir(QTABLE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(QTABLE_DIR, file), "r") as f:
                data = json.load(f)

            ep = int(data.get("episode", 0))
            ep_reward = data.get("episodeReward", 0)

            episode_map[ep] = ep_reward

    if not episode_map: return

    df = pd.DataFrame(
        list(episode_map.items()),
        columns=['Episode', 'EpisodeReward']
    ).sort_values('Episode')

    # smoothing (optional but useful)
    df['Rolling_Avg'] = df['EpisodeReward'].rolling(
        window=min(len(df), 10),
        min_periods=1
    ).mean()

    plt.figure(figsize=(12, 6))

    plt.plot(
        df['Episode'],
        df['EpisodeReward'],
        alpha=0.3,
        label='Raw Episode Reward'
    )

    plt.plot(
        df['Episode'],
        df['Rolling_Avg'],
        linewidth=2.5,
        label='Trend (SMA 10)'
    )

    plt.title("Episode Reward (Per Episode Performance)")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.6)

    save_plot("episode_reward.png")

# =========================
# 2. TOTAL VISITS PER EPISODE
# =========================
def plot_total_visits_per_episode():
    episode_map = {}
    if not os.path.exists(REPORT_DIR): return

    for ep_folder in os.listdir(REPORT_DIR):
        if not ep_folder.isdigit(): continue
        folder_path = os.path.join(REPORT_DIR, ep_folder)

        for file in os.listdir(folder_path):
            if "TargetDetectionReport" in file:
                total_visits = 0
                with open(os.path.join(folder_path, file), "r") as f:
                    for line in f:
                        match = re.search(r'T\d+,(\d+)', line)
                        if match:
                            total_visits += int(match.group(1))

                episode_map[int(ep_folder)] = total_visits

    if not episode_map: return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Visits']).sort_values('Episode')

    plt.figure(figsize=(12, 6))
    plt.fill_between(df['Episode'], df['Visits'], alpha=0.3)
    plt.plot(df['Episode'], df['Visits'], linewidth=2, marker='o', markersize=3)

    plt.title("Exploration Intensity: Total Target Visits per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Cumulative Visits")
    plt.grid(True, linestyle='--', alpha=0.5)

    save_plot("total_visits_per_episode.png")

# =========================
# 3. TARGET DETECTION
# =========================
def plot_total_target_found():
    episode_map = {}
    if not os.path.exists(REPORT_DIR): return

    for ep_folder in os.listdir(REPORT_DIR):
        if not ep_folder.isdigit(): continue
        folder_path = os.path.join(REPORT_DIR, ep_folder)

        for file in os.listdir(folder_path):
            if "TargetDetectionReport" in file:
                with open(os.path.join(folder_path, file), "r") as f:
                    content = f.read()
                    match = re.search(r'Total Target Found: (\d+)', content)
                    if match:
                        episode_map[int(ep_folder)] = int(match.group(1))

    if not episode_map: return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Targets']).sort_values('Episode')

    plt.figure(figsize=(14, 6))
    plt.fill_between(df['Episode'], df['Targets'], alpha=0.1)
    plt.plot(df['Episode'], df['Targets'], marker='o', markersize=4, linewidth=1.5)

    plt.title("Success Rate: Targets Found per Episode")
    plt.xlabel("Episode")
    plt.ylabel("Targets Found")
    plt.grid(axis='y', linestyle=':', alpha=0.8)

    save_plot("total_target_found_refined.png")

# =========================
# 4. STATE VISIT
# =========================
def plot_state_visit_cumulative():
    state_visit_map = {}
    if not os.path.exists(QTABLE_DIR): return

    for file in os.listdir(QTABLE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(QTABLE_DIR, file), "r") as f:
                data = json.load(f)
            for s in data.get("states", []):
                sid = s.get("state")
                visits = sum(s.get("visitCounts", []))
                state_visit_map[sid] = state_visit_map.get(sid, 0) + visits

    if not state_visit_map: return

    states = sorted(state_visit_map.keys())
    visits = [state_visit_map[s] for s in states]

    # BAR
    plt.figure(figsize=(12, 7))
    plt.bar(states, visits)
    plt.title("State Exploration Distribution (Bar)")
    plt.xlabel("State")
    plt.ylabel("Visits")
    save_plot("state_visit_bar.png")

    # LINE
    plt.figure(figsize=(12, 7))
    plt.plot(states, visits, marker='o')
    plt.title("State Exploration Distribution (Line)")
    plt.xlabel("State")
    plt.ylabel("Visits")
    plt.grid(True)
    save_plot("state_visit_line.png")

# =========================
# 5. TRAJECTORY (FIXED!!)
# =========================
def plot_trajectory_cumulative():
    trajectory_map = {}
    if not os.path.exists(REPORT_DIR): return

    for ep_folder in os.listdir(REPORT_DIR):
        if not ep_folder.isdigit(): continue
        folder_path = os.path.join(REPORT_DIR, ep_folder)

        for file in os.listdir(folder_path):
            if "TrajectoryFrequencyReport" in file:
                path = os.path.join(folder_path, file)

                try:
                    # 🔥 FIX HERE
                    df = pd.read_csv(path, header=None)

                    # force correct format
                    if df.shape[1] >= 2:
                        df = df.iloc[:, :2]
                        df.columns = ["Length", "Count"]
                    else:
                        continue

                    for _, row in df.iterrows():
                        length = int(row["Length"])
                        freq = int(row["Count"])
                        trajectory_map[length] = trajectory_map.get(length, 0) + freq

                except Exception as e:
                    print(f"Error reading {path}: {e}")
                    continue

    if not trajectory_map: return

    # ensure 1 exists
    if 1 not in trajectory_map:
        trajectory_map[1] = 0

    df_traj = pd.DataFrame(
        list(trajectory_map.items()),
        columns=['Length', 'Count']
    ).sort_values('Length')

    total_count = df_traj['Count'].sum()
    df_traj['Density'] = df_traj['Count'] / total_count

    # BAR
    plt.figure(figsize=(10, 6))
    plt.bar(df_traj['Length'], df_traj['Density'])
    plt.title("Trajectory Density (Bar)")
    plt.xlabel("Length")
    plt.ylabel("Density")
    save_plot("trajectory_bar.png")

    # LINE
    plt.figure(figsize=(10, 6))
    plt.plot(df_traj['Length'], df_traj['Density'], marker='o')
    plt.title("Trajectory Density (Line)")
    plt.xlabel("Length")
    plt.ylabel("Density")
    plt.grid(True)
    save_plot("trajectory_line.png")

# =========================
# EXECUTION
# =========================
if __name__ == "__main__":
    print("🚀 Starting visualization...")
    plot_total_reward()
    plot_episode_reward()   # 🔥 NEW
    plot_total_visits_per_episode()
    plot_total_target_found()
    plot_state_visit_cumulative()
    plot_trajectory_cumulative()
    print("✅ All plots generated successfully!")