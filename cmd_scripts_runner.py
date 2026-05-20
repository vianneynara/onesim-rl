import subprocess
import os

# Working directory
WORK_DIR = r"C:\Users\jarkom\Documents\Java\onesim-rl"

# # Commands to run (batch urnning)
# commands = [
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 11-16 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 17-22 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 17-22 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 17-22 -vc',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 17-22 -vc',
# ]

# Commands to run (batch urnning)
commands = [
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 11 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 12 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 13 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 14 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 15 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 16 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 17 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 18 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 19 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 20 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 21 -vc',
    r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 22 -vc',
]

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

# Open each command in a new Command Prompt window
for cmd in commands:
    full_cmd = (
        f'start "" cmd /k "'
        f'cd /d "{WORK_DIR}" '
        f'&& {cmd}"'
    )

    subprocess.Popen(full_cmd, shell=True)

print("Opened all command prompts.")