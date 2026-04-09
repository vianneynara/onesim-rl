import subprocess
import winsound

# =========================
# GLOBAL SETTINGS
# =========================
NUM_EPISODES = 500
START_NUM_EP = 1
BASE_CONFIG = "settings/RL.cfg"     # config file

# =========================
# 🔥 EXPERIMENT LIST
# =========================
EXPERIMENT_LIST = [
#     # =========================
#     # EPSILON
#     # =========================
    {"policy": "EPSILON", "rl_model": "QL"},
    {"policy": "EPSILON", "rl_model": "MC", "mc_mode": "FV"},
    {"policy": "EPSILON", "rl_model": "MC", "mc_mode": "EV"},

    # =========================
    # UCB (C = 1)
    # =========================
    {"policy": "UCB", "rl_model": "QL", "ucb_c": 1.0},
    {"policy": "UCB", "rl_model": "MC", "mc_mode": "FV", "ucb_c": 1.0},
    {"policy": "UCB", "rl_model": "MC", "mc_mode": "EV", "ucb_c": 1.0},

    # =========================
    # UCB (C = 2)
    # =========================
    {"policy": "UCB", "rl_model": "QL", "ucb_c": 2.0},
    {"policy": "UCB", "rl_model": "MC", "mc_mode": "FV", "ucb_c": 2.0},
    {"policy": "UCB", "rl_model": "MC", "mc_mode": "EV", "ucb_c": 2.0},

#     # =========================
#     # THOMPSON
#     # =========================
    {"policy": "THOMPSON", "rl_model": "QL"},
    {"policy": "THOMPSON", "rl_model": "MC", "mc_mode": "FV"},
    {"policy": "THOMPSON", "rl_model": "MC", "mc_mode": "EV"},
]

# =========================
# 🔊 SOUND ALERTS
# =========================
def alert_success():
    print("\n🎉 ALL EXPERIMENTS COMPLETE!")
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    for _ in range(3):
        winsound.Beep(2500, 200)
        winsound.Beep(1500, 200)

def alert_error():
    print("\n❌ SIMULATION CRASHED")
    winsound.MessageBeep(winsound.MB_ICONHAND)
    winsound.Beep(200, 1000)

# =========================
# 📁 FOLDER NAMING
# =========================
def generate_base_folder(config):
    # folder name
    name = f"NEW-D-{config['rl_model']}-{config['policy']}"

    if config["rl_model"] == "MC":
        name += f"-{config.get('mc_mode', 'EV')}"

    if config["policy"] == "UCB":
        name += f"-C{config.get('ucb_c', 1)}"

    return name

# =========================
# 🔥 BUILD OVERRIDES
# =========================
def build_overrides(ep, config, base_folder, save_prefix, episode_prefix):
    overrides = []

    # Scenario name
    overrides.append(f"Scenario.name=RL_{base_folder}_Ep_{ep}")

    # Load previous QTable
    if ep > 1:
        overrides.append(f"RLAgent.loadFileName={save_prefix}_{ep-1}")

    # Save config
    overrides.append(f"RLAgent.saveFileName={save_prefix}")
    overrides.append(f"RLAgent.episodeFileName={episode_prefix}")

    # Folder config
    overrides.append(f"RLAgent.baseFolder={base_folder}")
    overrides.append(f"RLAgent.currentEpisode={ep}")

    # Report folder
    overrides.append(f"Report.reportDir=reports/{base_folder}/{ep}")

    # =========================
    # POLICY SWITCH
    # =========================
    if config["policy"] == "EPSILON":
        overrides.append("RLAgent.behaviorPolicy=mcrltest.policy.EpsilonGreedyPolicy")

    elif config["policy"] == "UCB":
        overrides.append("RLAgent.behaviorPolicy=mcrltest.policy.UCBPolicy")
        overrides.append(f"BehaviorPolicy.UCB.c={config.get('ucb_c', 1)}")

    elif config["policy"] == "THOMPSON":
        overrides.append("RLAgent.behaviorPolicy=mcrltest.policy.ThompsonSamplingPolicy")

    # =========================
    # RL MODEL SWITCH
    # =========================
    if config["rl_model"] == "QL":
        overrides.append("RLAgent.rlModel=mcrltest.qModel.QLearningModel")

    elif config["rl_model"] == "MC":
        overrides.append("RLAgent.rlModel=mcrltest.qModel.MonteCarloModel")

        if config.get("mc_mode", "EV") == "FV":
            overrides.append("MonteCarlo.firstVisit=true")
        else:
            overrides.append("MonteCarlo.firstVisit=false")

    return "@@".join(overrides)

# =========================
# 📊 RUN PLOTTER
# =========================
def run_plotter(base_folder):
    print(f"\n📊 Plotting {base_folder}...")
    try:
        # plotter python file
        subprocess.run(["python", "multi_plotter.py", base_folder], check=True)
        print("✅ Plotting complete!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Plotter failed: {e}")

# =========================
# 🚀 RUN ONE EXPERIMENT
# =========================
def run_experiment(config):
    base_folder = generate_base_folder(config)
    save_prefix = f"{base_folder}_ep"
    episode_prefix = f"EPS-{base_folder}_ep"

    print("\n======================================")
    print(f"🚀 RUNNING EXPERIMENT: {base_folder}")
    print("======================================")

    for ep in range(START_NUM_EP, NUM_EPISODES + 1):
        print(f"➡️ Episode {ep}")

        overrides = build_overrides(ep, config, base_folder, save_prefix, episode_prefix)

        cmd = [
            r".\one.bat",
            "-b", "1",
            "-d", overrides,
            BASE_CONFIG
        ]

        try:
            subprocess.run(cmd, check=True, shell=True)
        except subprocess.CalledProcessError:
            alert_error()
            return

    print(f"✅ Finished Experiment: {base_folder}")

    # Auto plot after experiment
    run_plotter(base_folder)

# =========================
# 🎯 MAIN LOOP
# =========================
if __name__ == "__main__":
    for config in EXPERIMENT_LIST:
        run_experiment(config)

    alert_success()