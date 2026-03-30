import os
import json
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# =========================
# STYLE CONFIG
# =========================
plt.style.use('seaborn-v0_8-muted')
sns.set_context("notebook", font_scale=1.2)

BASE_FOLDER = "MC-FV-1_1"
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
    plt.plot(df['Episode'], df['Reward'], alpha=0.3, color='royalblue', label='Raw Reward')
    plt.plot(df['Episode'], df['Rolling_Avg'], color='darkblue', linewidth=2.5, label='Trend (SMA 10)')

    plt.title("Agent Learning Progress: Total Reward", fontsize=16, pad=20)
    plt.xlabel("Episode")
    plt.ylabel("Total Reward")
    plt.legend(frameon=True, loc='upper left')
    plt.grid(True, linestyle='--', alpha=0.6)
    save_plot("total_reward_refined.png")

# =========================
# 2. TARGET DETECTION
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
                    # Updated regex to be more robust [cite: 1]
                    match = re.search(r'Total Target Found: (\d+)', content)
                    if match:
                        episode_map[int(ep_folder)] = int(match.group(1))

    if not episode_map: return

    df = pd.DataFrame(list(episode_map.items()), columns=['Episode', 'Targets']).sort_values('Episode')

    plt.figure(figsize=(14, 6))
    plt.fill_between(df['Episode'], df['Targets'], color="seagreen", alpha=0.1)
    plt.plot(df['Episode'], df['Targets'], color="seagreen", marker='o', markersize=4, linewidth=1.5)

    plt.title("Success Rate: Targets Found per Episode", fontsize=16)
    plt.xlabel("Episode")
    plt.ylabel("Targets Found")
    plt.grid(axis='y', linestyle=':', alpha=0.8)
    save_plot("total_target_found_refined.png")

# =========================
# 3. STATE VISIT (FIXED COLORBAR)
# =========================
def plot_state_visit_cumulative():
    state_visit_map = {}
    if not os.path.exists(QTABLE_DIR): return

    for file in os.listdir(QTABLE_DIR):
        if file.endswith(".json"):
            with open(os.path.join(QTABLE_DIR, file), "r") as f:
                data = json.load(f)
            for s in data.get("states", []):
                # Summing visitCounts for both actions in each state [cite: 1]
                sid, visits = s.get("state"), sum(s.get("visitCounts", []))
                state_visit_map[sid] = state_visit_map.get(sid, 0) + visits

    if not state_visit_map: return

    states = sorted(state_visit_map.keys())
    visits = [state_visit_map[s] for s in states]

    fig, ax = plt.subplots(figsize=(12, 7))

    # Normalize visits for the colormap
    max_v = max(visits) if visits else 1
    norm = plt.Normalize(0, max_v)
    colors = plt.cm.plasma(norm(visits))

    bars = ax.bar(states, visits, color=colors, edgecolor='black', alpha=0.85)

    # FIXED: Added ax=ax to explicitly tell colorbar where to go
    sm = plt.cm.ScalarMappable(norm=norm, cmap='plasma')
    fig.colorbar(sm, ax=ax, label='Visit Density')

    ax.set_title("State Exploration Distribution", fontsize=16)
    ax.set_xlabel("State Identifier")
    ax.set_ylabel("Cumulative Visits")
    ax.set_xticks(states)
    save_plot("state_visit_refined.png")

# =========================
# 4. TRAJECTORY FREQUENCY
# =========================
def plot_trajectory_cumulative():
    trajectory_map = {}
    if not os.path.exists(REPORT_DIR): return

    for ep_folder in os.listdir(REPORT_DIR):
        folder_path = os.path.join(REPORT_DIR, ep_folder)
        if not ep_folder.isdigit(): continue
        for file in os.listdir(folder_path):
            if "TrajectoryFrequencyReport" in file:
                path = os.path.join(folder_path, file)
                try:
                    df = pd.read_csv(path)
                    # Aggregate trajectory counts across episodes [cite: 2]
                    for _, row in df.iterrows():
                        length, freq = row.iloc[0], row.iloc[1]
                        trajectory_map[length] = trajectory_map.get(length, 0) + freq
                except Exception: continue

    if not trajectory_map: return

    x = sorted(trajectory_map.keys())
    y = [trajectory_map[val] for val in x]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=x, y=y, hue=x, palette="magma", legend=False)

    plt.title("Trajectory Length Frequency Distribution", fontsize=16)
    plt.xlabel("Trajectory Length (Steps)")
    plt.ylabel("Total Frequency Across Episodes")
    save_plot("trajectory_refined.png")

# =========================
# EXECUTION
# =========================
if __name__ == "__main__":
    print("🚀 Starting fixed visualization...")
    plot_total_reward()
    plot_total_target_found()
    plot_state_visit_cumulative()
    plot_trajectory_cumulative()
    print("✅ All plots generated successfully!")