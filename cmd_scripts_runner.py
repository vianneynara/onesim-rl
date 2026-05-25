import subprocess
import os
from pathlib import Path

# Working directory - dynamically detect repo root where this script is located
WORK_DIR = Path(__file__).resolve().parent
VENV_ACTIVATE = WORK_DIR / ".venv" / "Scripts" / "activate.bat"

# -srp "D:\Developments+\Java\onesim-rl-data\reports"

# COMMAND-FOR: Running all of the Immobile Gaussian and Immobile Non-Stationary Gaussian
commands = [
    r'python pyrunner/batch_runner.py -pid lfe-g-ms@0 -c 36-43 -alg lfe-g-ms@0',
    r'python pyrunner/batch_runner.py -pid lfe-g-ms@1 -c 36-43 -alg lfe-g-ms@1',
    r'python pyrunner/batch_runner.py -pid ql-g-ms@0 -c 1-35 -alg ql-g-ms@0',
    r'python pyrunner/batch_runner.py -pid ql-g-ms@1 -c 1-35 -alg ql-g-ms@1',
    r'python pyrunner/batch_runner.py -pid lfe-nsg-ms@0 -c 36-43 -alg lfe-nsg-ms@0',
    r'python pyrunner/batch_runner.py -pid lfe-nsg-ms@1 -c 36-43 -alg lfe-nsg-ms@1',
    r'python pyrunner/batch_runner.py -pid ql-nsg-ms@0 -c 1-35 -alg ql-nsg-ms@0',
    r'python pyrunner/batch_runner.py -pid ql-nsg-ms@1 -c 1-35 -alg ql-nsg-ms@1',
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
