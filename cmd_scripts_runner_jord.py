import subprocess
import os

# Working directory
WORK_DIR = r"C:\Users\ZeroKampus\IdeaProjects\onesim-rl"

# # Commands to run (batch shifter)
# commands = [
#     r'python pyrunner/batch_shifter.py -pid mcn-c-ms@0',
#     r'python pyrunner/batch_shifter.py -pid mcn-c-ms@1',
#     r'python pyrunner/batch_shifter.py -pid mcn-p-ms@0',
#     r'python pyrunner/batch_shifter.py -pid mcn-p-ms@1',
# ]

# # Commands to run (batch shifter)
# commands = [
#     r'python pyrunner/group_key_upgrader.py -pid mcn-c-ms@0',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-c-ms@1',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-p-ms@0',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-p-ms@1',
# ]

# # Commands to run (batch running)
# # First Visit (fv=True)
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 1-13,15,17',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 1-13,15,17',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 1-13,15,17',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 1-13,15,17',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 19-35',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 19-35',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 19-35',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 19-35',
# ]
#
# # Commands to run (batch running)
# # First Visit (fv=False)
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 36-48,50,52',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 36-48,50,52',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 36-48,50,52',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 36-48,50,52',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 54-70',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 54-70',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 54-70',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 54-70',
# ]

# # Commands to run (batch running)
# # UCB EC 1.25, 1.75, 2.25
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 14,16,18',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 14,16,18',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 14,16,18',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 14,16,18',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 49,51,53',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 49,51,53',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 49,51,53',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 49,51,53',
# ]


# # Verified Continue
# # Commands to run (batch running)
# # First Visit (fv=True)
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 1-13,15,17 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 1-13,15,17 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 1-13,15,17 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 1-13,15,17 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 19-35 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 19-35 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 19-35 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 19-35 -vc',
# ]
#
# Commands to run (batch running)
# First Visit (fv=False)
commands = [
    r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 36-48,50,52 -vc',
    r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 36-48,50,52 -vc',
    r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 36-48,50,52 -vc',
    r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 36-48,50,52 -vc',
    r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 54-70 -vc',
    r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 54-70 -vc',
    r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 54-70 -vc',
    r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 54-70 -vc',
]
#
# # Commands to run (batch running)
# # UCB EC 1.25, 1.75, 2.25
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 14,16,18 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 14,16,18 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 14,16,18 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 14,16,18 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 49,51,53 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 49,51,53 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 49,51,53 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 49,51,53 -vc',
# ]


# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@0 --title "Lévy Flight on Stochastic Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@1 --title "Lévy Flight on Fixed Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@0 --title "Lévy Flight on Stochastic Stationary Poisson Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@1 --title "Lévy Flight on Fixed Stationary Poisson Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@0 --title "Q-Learning on Stochastic Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@1 --title "Q-Learning on Fixed Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@0 --title "Q-Learning on Stochastic Stationary Poisson Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@1 --title "Q-Learning on Fixed Stationary Poisson Distributed Targets" --describe',
# ]

# # Episode Extender
# # Commands to run (batch running)
# # First Visit (fv=True)
# commands = [
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@0 -c 1-13,15,17 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@1 -c 1-13,15,17 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@0 -c 1-13,15,17 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@1 -c 1-13,15,17 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@0 -c 19-35 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@1 -c 19-35 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@0 -c 19-35 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@1 -c 19-35 --toepisodes 750',
# ]

# # Commands to run (batch running)
# # First Visit (fv=False)
# commands = [
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@0 -c 36-48,50,52 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@1 -c 36-48,50,52 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@0 -c 36-48,50,52 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@1 -c 36-48,50,52 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@0 -c 54-70 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-c-ms@1 -c 54-70 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@0 -c 54-70 --toepisodes 750',
#     r'python pyrunner/episode_extender.py -pid mcn-p-ms@1 -c 54-70 --toepisodes 750',
# ]

# Open each command in a new Command Prompt window
for cmd in commands:
    full_cmd = (
        f'start "" cmd /k "'
        f'cd /d "{WORK_DIR}" '
        f'&& {cmd}"'
    )

    subprocess.Popen(full_cmd, shell=True)

print("Opened all command prompts.")