import os
import sys
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# 🔥 STYLE CONFIG
# =========================
plt.style.use('seaborn-v0_8-muted')
sns.set_context("talk", font_scale=1.3)

# =========================
# 📁 GET FOLDER FROM ARG
# =========================
if len(sys.argv) > 1:
    BASE_FOLDER = sys.argv[1]
else:
    print("❌ No BASE_FOLDER provided!")
    exit()

print(f"📂 Using: {BASE_FOLDER}")

QTABLE_DIR = f"data/qtable/{BASE_FOLDER}"
REPORT_DIR = f"reports/{BASE_FOLDER}"
PLOT_DIR = f"data/plotter/{BASE_FOLDER}"

os.makedirs(PLOT_DIR, exist_ok=True)

# =========================
# 💾 SAVE
# =========================
def save_plot(name):
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, name)
    plt.savefig(path, dpi=300)
    plt.close()
    print(f"Saved → {path}")

# =========================
# 📊 1. TOTAL REWARD
# =========================
def plot_total_reward():
    episode_map = {}

    if not os.path.exists(QTABLE_DIR):
        return

    for file in os.listdir(QTABLE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(QTABLE_DIR, file), "r") as f:
                data = json.load(f)
                episode_map[int(data.get("episode", 0))] = data.get("totalReward", 0)

    if not episode_map:
        return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Reward'])
    df = df.sort_values('Episode')

    df['Rolling'] = df['Reward'].rolling(window=min(len(df), 20), min_periods=1).mean()

    plt.figure(figsize=(14, 7))
    plt.plot(df['Episode'], df['Reward'], alpha=0.25, label='Raw')
    plt.plot(df['Episode'], df['Rolling'], linewidth=3, label='Trend')

    plt.title("Total Reward")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.legend()
    plt.grid(True)

    save_plot("total_reward.png")

# =========================
# 📊 2. EPISODE REWARD
# =========================
def plot_episode_reward():
    episode_map = {}

    if not os.path.exists(QTABLE_DIR):
        return

    for file in os.listdir(QTABLE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(QTABLE_DIR, file), "r") as f:
                data = json.load(f)

            episode_map[int(data.get("episode", 0))] = data.get("episodeReward", 0)

    if not episode_map:
        return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Reward'])
    df = df.sort_values('Episode')

    df['Rolling'] = df['Reward'].rolling(window=min(len(df), 20), min_periods=1).mean()

    plt.figure(figsize=(14, 7))
    plt.plot(df['Episode'], df['Reward'], alpha=0.25)
    plt.plot(df['Episode'], df['Rolling'], linewidth=3)

    plt.title("Episode Reward")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.grid(True)

    save_plot("episode_reward.png")

# =========================
# 📊 3. TARGET FOUND
# =========================
def plot_target_found():
    episode_map = {}

    if not os.path.exists(REPORT_DIR):
        return

    for ep_folder in os.listdir(REPORT_DIR):
        if not ep_folder.isdigit():
            continue

        folder_path = os.path.join(REPORT_DIR, ep_folder)

        for file in os.listdir(folder_path):
            if "TargetDetectionReport" in file:
                with open(os.path.join(folder_path, file), "r") as f:
                    content = f.read()
                    match = re.search(r'Total Target Found: (\d+)', content)
                    if match:
                        episode_map[int(ep_folder)] = int(match.group(1))

    if not episode_map:
        return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Targets'])
    df = df.sort_values('Episode')

    plt.figure(figsize=(14, 7))
    plt.plot(df['Episode'], df['Targets'], marker='o', linewidth=2)

    plt.title("Targets Found")
    plt.xlabel("Episode")
    plt.ylabel("Targets")
    plt.grid(True)

    save_plot("targets_found.png")

# =========================
# 📊 4. VISITS
# =========================
def plot_total_visits():
    episode_map = {}

    if not os.path.exists(REPORT_DIR):
        return

    for ep_folder in os.listdir(REPORT_DIR):
        if not ep_folder.isdigit():
            continue

        folder_path = os.path.join(REPORT_DIR, ep_folder)

        for file in os.listdir(folder_path):
            if "TargetDetectionReport" in file:
                total = 0
                with open(os.path.join(folder_path, file), "r") as f:
                    for line in f:
                        m = re.search(r'T\d+,(\d+)', line)
                        if m:
                            total += int(m.group(1))

                episode_map[int(ep_folder)] = total

    if not episode_map:
        return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Visits'])
    df = df.sort_values('Episode')

    plt.figure(figsize=(14, 7))
    plt.plot(df['Episode'], df['Visits'], linewidth=2)

    plt.title("Total Visits")
    plt.xlabel("Episode")
    plt.ylabel("Visits")
    plt.grid(True)

    save_plot("total_visits.png")

# =========================
# 🔥 5. TRAJECTORY (FIXED)
# =========================
def plot_trajectory_cumulative():
    trajectory_map = {}

    if not os.path.exists(REPORT_DIR):
        return

    for ep_folder in os.listdir(REPORT_DIR):
        if not ep_folder.isdigit():
            continue

        folder_path = os.path.join(REPORT_DIR, ep_folder)

        for file in os.listdir(folder_path):
            if "TrajectoryFrequencyReport" in file:
                path = os.path.join(folder_path, file)

                try:
                    df = pd.read_csv(path, header=None)

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

    if not trajectory_map:
        return

    if 1 not in trajectory_map:
        trajectory_map[1] = 0

    df_traj = pd.DataFrame(
        list(trajectory_map.items()),
        columns=['Length', 'Count']
    ).sort_values('Length')

    total = df_traj['Count'].sum()
    df_traj['Density'] = df_traj['Count'] / total

    # BAR
    plt.figure(figsize=(12, 6))
    plt.bar(df_traj['Length'], df_traj['Density'])
    plt.title("Trajectory Density (Bar)")
    plt.xlabel("Length")
    plt.ylabel("Density")
    save_plot("trajectory_bar.png")

    # LINE
    plt.figure(figsize=(12, 6))
    plt.plot(df_traj['Length'], df_traj['Density'], marker='o')
    plt.title("Trajectory Density (Line)")
    plt.xlabel("Length")
    plt.ylabel("Density")
    plt.grid(True)
    save_plot("trajectory_line.png")

# =========================
# 🚀 MAIN
# =========================
if __name__ == "__main__":
    print("🚀 Generating plots...")

    plot_total_reward()
    plot_episode_reward()
    plot_target_found()
    plot_total_visits()
    plot_trajectory_cumulative()  # 🔥 BACK

    print("✅ All plots generated!")