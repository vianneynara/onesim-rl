import subprocess
import os
from pathlib import Path

# Working directory - dynamically detect repo root where this script is located
WORK_DIR = Path(__file__).resolve().parent
VENV_ACTIVATE = WORK_DIR / ".venv" / "Scripts" / "activate.bat"

# # Commands to run (batch urnning)
# commands = [
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 17-22 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 17-22 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 17-22 -vc',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@0 --title "Lévy Flight on Resampled Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@1 --title "Lévy Flight on Fixed Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@0 --title "Lévy Flight on Resampled Stationary Poisson Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@1 --title "Lévy Flight on Fixed Stationary Poisson Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@0 --title "Q-Learning on Resampled Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@1 --title "Q-Learning on Fixed Stationary Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@0 --title "Q-Learning on Resampled Stationary Poisson Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@1 --title "Q-Learning on Fixed Stationary Poisson Distributed Targets" --describe',
# ]

# commands = [
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 11-13 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 14-15 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 16-19 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 20-22 -alg ql-c-ms@1 -vc',
# ]

# commands = [
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 25 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 32 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -c 27 -alg ql-p-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -c 31 -alg ql-p-ms@0 -vc',
# ]

commands = [
    r'python pyrunner/episode_extender.py -pid ql-c-ms@0 -c 25 --revertto 100',
    r'python pyrunner/episode_extender.py -pid ql-c-ms@0 -c 32 --revertto 100',
    r'python pyrunner/episode_extender.py -pid ql-p-ms@0 -c 27 --revertto 100',
    r'python pyrunner/episode_extender.py -pid ql-p-ms@0 -c 31 --revertto 100',
]

# Open each command in a new Command Prompt window
for command in commands:
    full_cmd = (
        f'start "" cmd /k "cd /d \"{WORK_DIR}\" && '
        f'call \"{VENV_ACTIVATE}\" && '
        f'{command}"'
    )

    subprocess.Popen(full_cmd, shell=True)

print("Opened all command prompts.")
