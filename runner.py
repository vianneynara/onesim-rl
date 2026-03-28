import subprocess

NUM_EPISODES = 2
BASE_CONFIG = "settings/RLTest.cfg"

SAVE_PREFIX = "test-cd-1_ep"
EPISODE_PREFIX = "t-cd-1_ep"
BASE_FOLDER = "test-cd-1"

def run_simulation():

    for ep in range(1, NUM_EPISODES + 1):

        print(f"\n🚀 Starting Episode {ep}")

        overrides = f"Scenario.name=RL_Test_Ep_{ep}"

        # 🔁 Load previous QTable
        if ep > 1:
            overrides += f"@@RLAgent.loadFileName={SAVE_PREFIX}_{ep-1}"

        # 💾 Save settings
        overrides += f"@@RLAgent.saveFileName={SAVE_PREFIX}"
        overrides += f"@@RLAgent.episodeFileName={EPISODE_PREFIX}"

        # 📁 Folder control
        overrides += f"@@RLAgent.baseFolder={BASE_FOLDER}"
        overrides += f"@@RLAgent.currentEpisode={ep}"

        # 📊 Report folder (NO JAVA CHANGE NEEDED)
        overrides += f"@@Report.reportDir=reports/{BASE_FOLDER}/{ep}"

#         cmd = [
#             r".\one.bat",
#             "1",
#             "-d", overrides,
#             BASE_CONFIG
#         ]

        cmd = [
            r".\one.bat",
            "-b","1",
            "-d", overrides,
            BASE_CONFIG
        ]

        try:
            subprocess.run(cmd, check=True, shell=True)
            print(f"✅ Finished Episode {ep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            break


if __name__ == "__main__":
    run_simulation()