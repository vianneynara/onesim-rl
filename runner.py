import subprocess
import winsound  # Built-in Windows library for sound

NUM_EPISODES = 1
BASE_CONFIG = "settings/RLTest.cfg"

# SAVE_PREFIX = "MC-FV-2_ep"
# EPISODE_PREFIX = "EPS-MC-FV-2_ep"
# BASE_FOLDER = "MC-FV-2"

# SAVE_PREFIX = "MC-EV-2_ep"
# EPISODE_PREFIX = "EPS-MC-EV-2_ep"
# BASE_FOLDER = "MC-EV-2_1"

# SAVE_PREFIX = "MC-EV-NR_ep"
# EPISODE_PREFIX = "EPS-MC-EV-NR_ep"
# BASE_FOLDER = "MC-EV-NR_1"

SAVE_PREFIX = "test-cd-1_ep"
EPISODE_PREFIX = "t-cd-1_ep"
BASE_FOLDER = "test-cd-1"

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