import subprocess

# --- Configuration ---
NUM_EPISODES = 3
BASE_CONFIG = "settings/RLTest.cfg"
# This MUST match the RLAgent.saveFileName in your .cfg
# SAVE_PREFIX = "montst-2_ep"
# EPISODE_PREFIX = "EpS-mont_ep"

SAVE_PREFIX = "qlrn-2_ep"
EPISODE_PREFIX = "EpS-qlrn-2_ep"

def run_simulation():
    for ep in range(1, NUM_EPISODES + 1):
        print(f"\n🚀 Starting Episode {ep}...")

        # 1. Base command - KEEP THE PREFIX CONSTANT
        overrides = f"Scenario.name=RLTest_Ep_{ep}_@%%RLAgent.rlModel%%-@%%MonteCarlo.firstVisit%%"

        # 2. Handoff Logic
        if ep > 1:
            # We load the file saved by the PREVIOUS episode
            # The simulator automatically saved Ep 1 as 'tt_ep_1'
            load_val = f"{SAVE_PREFIX}_{ep-1}"
            overrides += f"@@RLAgent.loadFileName={load_val}"

        # We tell it to save using the BASE prefix.
        # The simulator will append '_1', '_2', etc., automatically.
        overrides += f"@@RLAgent.saveFileName={SAVE_PREFIX}"
        overrides += f"@@RLAgent.episodeFileName={EPISODE_PREFIX}"

        cmd = [
            r".\one.bat",
            "-b", "1",
            "-d", overrides,
            BASE_CONFIG
        ]

#         cmd = [
#                     r".\one.bat",
#                     "1",
#                     "-d", overrides,
#                     BASE_CONFIG
#                 ]

        try:
            subprocess.run(cmd, check=True, shell=True)
            print(f"✅ Finished Episode {ep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    run_simulation()