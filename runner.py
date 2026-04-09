import subprocess
import winsound  # Built-in Windows library for sound

NUM_EPISODES = 500
BASE_CONFIG = "settings/RLTest.cfg"

# 1
START_NUM_EP = 1

# belum di pakai
# SCENARIO_NAME = "QL-UCB"

# SAVE_PREFIX = "D-MC-EPS-EV-1_ep"
# EPISODE_PREFIX = "EPS-D-MC-EPS-EV-1_ep"
# BASE_FOLDER = "D-MC-EPS-EV-1"

# SAVE_PREFIX = "D-MC-EPS-FV-1_ep"
# EPISODE_PREFIX = "EPS-D-MC-EPS-FV-1_ep"
# BASE_FOLDER = "D-MC-EPS-FV-1"
#
# SAVE_PREFIX = "D-MC-THS-EV-1_ep"
# EPISODE_PREFIX = "EPS-D-MC-THS-EV-1_ep"
# BASE_FOLDER = "D-MC-THS-EV-1"
#
# SAVE_PREFIX = "D-MC-THS-FV-1_ep"
# EPISODE_PREFIX = "EPS-D-MC-THS-FV-1_ep"
# BASE_FOLDER = "D-MC-THS-FV-1"
#
SAVE_PREFIX = "D-MC-UCB.C1-EV-1_ep"
EPISODE_PREFIX = "EPS-D-MC-UCB.C1-EV-1_ep"
BASE_FOLDER = "D-MC-UCB.C1-EV-1"
#
# SAVE_PREFIX = "D-MC-UCB.C1-FV-1_ep"
# EPISODE_PREFIX = "EPS-D-MC-UCB.C1-FV-1_ep"
# BASE_FOLDER = "D-MC-UCB.C1-FV-1"
#
# SAVE_PREFIX = "D-MC-UCB.C2-EV-1_ep"
# EPISODE_PREFIX = "EPS-D-MC-UCB.C2-EV-1_ep"
# BASE_FOLDER = "D-MC-UCB.C2-EV-1"
#
# SAVE_PREFIX = "D-MC-UCB.C2-FV-1_ep"
# EPISODE_PREFIX = "EPS-D-MC-UCB.C2-FV-1_ep"
# BASE_FOLDER = "D-MC-UCB.C2-FV-1"
#
# # QL
#
# SAVE_PREFIX = "D-QL-EPS-1_ep"
# EPISODE_PREFIX = "EPS-D-QL-EPS-1_ep"
# BASE_FOLDER = "D-QL-EPS-1"
#
# SAVE_PREFIX = "D-QL-THS-1_ep"
# EPISODE_PREFIX = "EPS-D-QL-THS-1_ep"
# BASE_FOLDER = "D-QL-THS-1"
#
# SAVE_PREFIX = "D-QL-UCB.C1-1_ep"
# EPISODE_PREFIX = "EPS-D-QL-UCB.C1-1_ep"
# BASE_FOLDER = "D-QL-UCB.C1-1"
#
# SAVE_PREFIX = "D-QL-UCB.C2-1_ep"
# EPISODE_PREFIX = "EPS-D-QL-UCB.C2-1_ep"
# BASE_FOLDER = "D-QL-UCB.C2-1"

def alert_success():
    """Plays a loud, attention-grabbing 'Mission Complete' sound."""
    print("\n🎉 ALL EPISODES COMPLETE!")
    # Play the Windows 'Exclamation' system sound first
    winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

    # Then play a sequence of 3 rapid high-pitched beeps
    for _ in range(3):
        winsound.Beep(2500, 200) # High pitch (2500Hz) is very piercing
        winsound.Beep(1500, 200)

def alert_error():
    """Plays a low-pitched warning drone."""
    print("\n❌ SIMULATION CRASHED")
    winsound.MessageBeep(winsound.MB_ICONHAND) # Windows 'Critical Stop' sound
    winsound.Beep(200, 1000) # Long, low 200Hz drone

def run_simulation():
    for ep in range(START_NUM_EP, NUM_EPISODES + 1):
        print(f"\n🚀 Starting Episode {ep}")

        overrides = f"Scenario.name=RL_{BASE_FOLDER}_Ep_{ep}"

        # 🔁 Load previous QTable
        if ep > 1:
            overrides += f"@@RLAgent.loadFileName={SAVE_PREFIX}_{ep-1}"

        # 💾 Save settings
        overrides += f"@@RLAgent.saveFileName={SAVE_PREFIX}"
        overrides += f"@@RLAgent.episodeFileName={EPISODE_PREFIX}"

        # 📁 Folder control
        overrides += f"@@RLAgent.baseFolder={BASE_FOLDER}"
        overrides += f"@@RLAgent.currentEpisode={ep}"

        # 📊 Report folder
        overrides += f"@@Report.reportDir=reports/{BASE_FOLDER}/{ep}"

        cmd = [
            r".\one.bat",
            "-b", "1",
            "-d", overrides,
            BASE_CONFIG
        ]

#         cmd = [
#             r".\one.bat",
#             "1",
#             "-d", overrides,
#             BASE_CONFIG
#         ]

        try:
            subprocess.run(cmd, check=True, shell=True)
            print(f"✅ Finished Episode {ep}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error: {e}")
            alert_error() # 🔊 Play the loud error sound
            return

    # 🔊 SUCCESS NOTIFICATION
    alert_success()

if __name__ == "__main__":
    run_simulation()