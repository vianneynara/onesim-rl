import subprocess
import os
from pathlib import Path

# Working directory - dynamically detect repo root where this script is located
WORK_DIR = Path(__file__).resolve().parent
VENV_ACTIVATE = WORK_DIR / ".venv" / "Scripts" / "activate.bat"

################################################################################
# RERUNNING pid of LFE and QL with env setting of clustered.
################################################################################

# # LFE
# commands = [
#     r'python pyrunner/batch_runner.py -pid lfe-c-ms@0 -c 36-43 -alg lfe-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid lfe-c-ms@1 -c 36-43 -alg lfe-c-ms@1 -vc',
# ]

# QL
# commands = [
#     # Randomized Seed
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 1-5 -alg ql-c-ms@0',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 6-10 -alg ql-c-ms@0',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 11-16 -alg ql-c-ms@0',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 17-22 -alg ql-c-ms@0',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 23-27 -alg ql-c-ms@0',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 28-35 -alg ql-c-ms@0',
#     # Fixed Seed
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 1-5 -alg ql-c-ms@1',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 6-10 -alg ql-c-ms@1',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 11-16 -alg ql-c-ms@1',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 17-22 -alg ql-c-ms@1',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 23-27 -alg ql-c-ms@1',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 28-35 -alg ql-c-ms@1',
# ]

# commands = [
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 35 -alg ql-c-ms@0',
# ]

################################################################################
# BASE SIMULATIONS (750 EPISODES), INITIAL PLOTTING AND INITIAL TRAJECTORY AGGREGATOR
################################################################################

# commands = [
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@0 --title "Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@1 --title "Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@0 --title "Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@1 --title "Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@0 --title "Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@1 --title "Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@0 --title "Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@1 --title "Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# # ]
#
# # commands = [
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

### AFTER ABOVE, MERGE.

################################################################################
# RUNNING BEST OF EACH GROUP, of 1 day, 2 days, 3 days, 7 days.

## Thomas Clustered, Randomized Seed: (lf: 36, ql:2,11,25,35)

### To be run on 7 days, 3 days, 2 days, 1 day.
# commands = [
#     r'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@0 -c 36 -alg lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -c 2 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -c 11 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -c 25 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -c 35 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc',
# # ]
# # commands = [
#     r'python pyrunner/batch_runner.py -pid 3d-cont-lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=259200" -c 36 -alg lfe-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 2 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 11 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 25 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 35 -alg ql-c-ms@0 -vc',
# # ]
#
# # commands = [
#     r'python pyrunner/batch_runner.py -pid 2d-cont-lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=172800" -c 36 -alg lfe-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 2 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 11 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 25 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 35 -alg ql-c-ms@0 -vc',
# # ]
# # commands = [
#     r'python pyrunner/batch_runner.py -pid 1d-cont-lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=86400" -c 36 -alg lfe-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 2 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 11 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 25 -alg ql-c-ms@0 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 35 -alg ql-c-ms@0 -vc',
# ]

## Thomas Clustered, Fixed Seed: (lf: 36, ql: 11,35,25,36)

### To be run on 7 days, 3 days, 2 days, 1 day.
# commands = [
#     r'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@1 -c 36 -alg lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -c 2 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -c 11 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -c 25 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc',
#     r'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -c 35 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc',
# # ]
# # commands = [
#     r'python pyrunner/batch_runner.py -pid 3d-cont-lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=259200" -c 36 -alg lfe-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 2 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 11 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 25 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -c 35 -alg ql-c-ms@1 -vc',
# # ]
#
# # commands = [
#     r'python pyrunner/batch_runner.py -pid 2d-cont-lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=172800" -c 36 -alg lfe-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 2 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 11 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 25 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -c 35 -alg ql-c-ms@1 -vc',
# # ]
# # commands = [
#     r'python pyrunner/batch_runner.py -pid 1d-cont-lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=86400" -c 36 -alg lfe-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 2 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 11 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 25 -alg ql-c-ms@1 -vc',
#     r'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -c 35 -alg ql-c-ms@1 -vc',
# ]

################################################################################
# CONT SIMULATIONS (NEXT 100 EPISODES @ 7 DAYS), INITIAL PLOTTING AND INITIAL TRAJECTORY AGGREGATOR
################################################################################

# commands = [
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-c-ms@0 --title "Best Performing Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-c-ms@1 --title "Best Performing Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-p-ms@0 --title "Best Performing Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-p-ms@1 --title "Best Performing Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-c-ms@0 --title "Best Performing Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-c-ms@1 --title "Best Performing Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-p-ms@0 --title "Best Performing Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-p-ms@1 --title "Best Performing Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# # ]
# #
# # commands = [
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

### AFTER ABOVE, MERGE

################################################################################
# CONT SIMULATIONS (NEXT 100 EPISODES @ 1 DAY), INITIAL PLOTTING AND INITIAL TRAJECTORY AGGREGATOR
################################################################################

# # COMMAND-FOR: running plotters
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-lfe-c-ms@0 --title "Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-lfe-c-ms@1 --title "Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-lfe-p-ms@0 --title "Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-lfe-p-ms@1 --title "Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-ql-c-ms@0 --title "Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-ql-c-ms@1 --title "Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-ql-p-ms@0 --title "Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 1d-cont-ql-p-ms@1 --title "Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# # ]
# #
# # commands = [
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

### AFTER ABOVE, MERGE

################################################################################
# CONT SIMULATIONS (NEXT 100 EPISODES @ 2 DAY), INITIAL PLOTTING AND INITIAL TRAJECTORY AGGREGATOR
################################################################################

# # COMMAND-FOR: running plotters
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-lfe-c-ms@0 --title "Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-lfe-c-ms@1 --title "Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-lfe-p-ms@0 --title "Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-lfe-p-ms@1 --title "Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-ql-c-ms@0 --title "Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-ql-c-ms@1 --title "Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-ql-p-ms@0 --title "Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 2d-cont-ql-p-ms@1 --title "Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# # ]
# #
# # commands = [
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 2d-cont-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

### AFTER ABOVE, MERGE

################################################################################
# CONT SIMULATIONS (NEXT 100 EPISODES @ 3 DAY), INITIAL PLOTTING AND INITIAL TRAJECTORY AGGREGATOR
################################################################################

# # COMMAND-FOR: running plotters
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-c-ms@0 --title "Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-c-ms@1 --title "Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-p-ms@0 --title "Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-p-ms@1 --title "Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-c-ms@0 --title "Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-c-ms@1 --title "Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-p-ms@0 --title "Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-p-ms@1 --title "Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# # ]
# #
# # commands = [
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

### AFTER ABOVE, MERGE

# placeholder command
commands = []

# Open each command in a new Command Prompt window
for command in commands:
    full_cmd = (
        f'start "" cmd /k "cd /d \"{WORK_DIR}\" && '
        f'call \"{VENV_ACTIVATE}\" && '
        f'{command}"'
    )

    subprocess.Popen(full_cmd, shell=True)

print("Opened all command prompts.")
