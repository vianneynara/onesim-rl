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
    # TCP Randomized Seed
    # r'python pyrunner/batch_runner.py -pid lfe-c-ms@0 -alg lfe-c-ms@0 -c 55-56',
    # r'python pyrunner/batch_runner.py -pid lfe-c-ms@0 -alg lfe-c-ms@0 -c 57-58',
    # r'python pyrunner/batch_runner.py -pid lfe-c-ms@0 -alg lfe-c-ms@0 -c 59-60',
    # r'python pyrunner/batch_runner.py -pid lfe-c-ms@0 -alg lfe-c-ms@0 -c 61-62',
# ]

# QL - TCP (Thomas Cluster Process)
# commands = [
#     # TCP Randomized Seed
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 28-32',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 33-37',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 36-42',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 43-48',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@0 -alg ql-c-ms@0 -c 49-54',
#     # TCP Fixed Seed
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 28-32',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 33-37',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 36-42',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 43-48',
#     r'python pyrunner/batch_runner.py -pid ql-c-ms@1 -alg ql-c-ms@1 -c 49-54',
# ]

# QL - HPP (Homogenous Poisson Process)
# commands = [
#     # HPP Randomized Seed
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 28-32',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 33-37',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 36-42',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 43-48',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@0 -alg ql-p-ms@0 -c 49-54',
#     # HPP Fixed Seed
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 28-32',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 33-37',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 36-42',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 43-48',
#     r'python pyrunner/batch_runner.py -pid ql-p-ms@1 -alg ql-p-ms@1 -c 49-54',
# ]

################################################################################
# BASE SIMULATIONS (300 EPISODES), INITIAL PLOTTING AND INITIAL TRAJECTORY AGGREGATOR
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

# ```sh
# python pyplotters/summary_merger.py -mf lfe-c-ms@0 -mt ql-c-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf lfe-c-ms@1 -mt ql-c-ms@1 --mvplots
# python pyplotters/summary_merger.py -mf lfe-p-ms@0 -mt ql-p-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf lfe-p-ms@1 -mt ql-p-ms@1 --mvplots
#
# ```

### THEN ANALYZE BEST PERFORMANCE PER GROUP.

# ```sh
# python pyplotters/bestof_plotter.py -pid ql-c-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid ql-c-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
# python pyplotters/bestof_plotter.py -pid ql-p-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid ql-p-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'
#
# ```

## Best Configurations of Each Environment per Group
""" Fill with 5 elements, FIRST element is Levy Flight's Group, THE REST is the learning models' groups."""
TCP_0 = []
TCP_1 = []
HPP_0 = []
HPP_1 = []

# commands = [
#     # Thomas Clustering, Randomized Seed (pid: ql-c-ms@0)
#     f'python pyplotters/trajectory_aggregator.py -pid ql-c-ms@0 --uselastepisode --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets (300 eps)" --describe --compareall -c {",".join(TCP_0)}',
#     # Thomas Clustering, Fixed Seed (pid: ql-c-ms@1)
#     f'python pyplotters/trajectory_aggregator.py -pid ql-c-ms@1 --uselastepisode --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets (300 eps)" --describe --compareall -c {",".join(TCP_1)}',
#     # Homogenous Poisson, Randomized Seed (pid: ql-p-ms@0)
#     f'python pyplotters/trajectory_aggregator.py -pid ql-p-ms@0 --uselastepisode --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets (300 eps)" --describe --compareall -c {",".join(HPP_0)}',
#     # Homogenous Poisson, Fixed Seed (pid: ql-p-ms@1)
#     f'python pyplotters/trajectory_aggregator.py -pid ql-p-ms@1 --uselastepisode --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets (300 eps)" --describe --compareall -c {",".join(HPP_1)}'
# ]

################################################################################
# EXTRACTING MODELS FROM THE BEST ONES (7 days, 3 days, 2 days, 1 day)
################################################################################

# LFE

# commands = [
#     f'py .\pyrunner\model_extractor.py -pid lfe-c-ms@0 --ofepisode 300 --aspid "cont-lfe-c-ms@0" -es 100 --prepfor "qlm_rth=True" -c {TCP_0[0]}',
#     f'py .\pyrunner\model_extractor.py -pid lfe-c-ms@1 --ofepisode 300 --aspid "cont-lfe-c-ms@1" -es 100 --prepfor "qlm_rth=True" -c {TCP_1[0]}',
#     f'py .\pyrunner\model_extractor.py -pid lfe-p-ms@0 --ofepisode 300 --aspid "cont-lfe-p-ms@0" -es 100 --prepfor "qlm_rth=True" -c {HPP_0[0]}',
#     f'py .\pyrunner\model_extractor.py -pid lfe-p-ms@1 --ofepisode 300 --aspid "cont-lfe-p-ms@1" -es 100 --prepfor "qlm_rth=True" -c {HPP_1[0]}',
# ]

# QL

## PID: 7 days/cont-
# commands = [
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@0 --ofepisode 300 --aspid "cont-ql-c-ms@0" -es 100 --prepfor "qlm_rth=True" -c {TCP_0[1]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@1 --ofepisode 300 --aspid "cont-ql-c-ms@1" -es 100 --prepfor "qlm_rth=True" -c {TCP_1[1]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@0 --ofepisode 300 --aspid "cont-ql-p-ms@0" -es 100 --prepfor "qlm_rth=True" -c {HPP_0[1]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@1 --ofepisode 300 --aspid "cont-ql-p-ms@1" -es 100 --prepfor "qlm_rth=True" -c {HPP_1[1]}',
# ]

## PID: 3 days/3d-cont-
# commands = [
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@0 --ofepisode 300 --aspid "3d-cont-ql-c-ms@0" -es 100 --prepfor "qlm_rth=True" -c {TCP_0[2]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@1 --ofepisode 300 --aspid "3d-cont-ql-c-ms@1" -es 100 --prepfor "qlm_rth=True" -c {TCP_1[2]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@0 --ofepisode 300 --aspid "3d-cont-ql-p-ms@0" -es 100 --prepfor "qlm_rth=True" -c {HPP_0[2]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@1 --ofepisode 300 --aspid "3d-cont-ql-p-ms@1" -es 100 --prepfor "qlm_rth=True" -c {HPP_1[2]}',
# ]

## PID: 2 days/2d-cont-
# commands = [
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@0 --ofepisode 300 --aspid "2d-cont-ql-c-ms@0" -es 100 --prepfor "qlm_rth=True" -c {TCP_0[3]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@1 --ofepisode 300 --aspid "2d-cont-ql-c-ms@1" -es 100 --prepfor "qlm_rth=True" -c {TCP_1[3]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@0 --ofepisode 300 --aspid "2d-cont-ql-p-ms@0" -es 100 --prepfor "qlm_rth=True" -c {HPP_0[3]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@1 --ofepisode 300 --aspid "2d-cont-ql-p-ms@1" -es 100 --prepfor "qlm_rth=True" -c {HPP_1[3]}',
# ]

## PID: 1 day/1d-cont-
# commands = [
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@0 --ofepisode 300 --aspid "1d-cont-ql-c-ms@0" -es 100 --prepfor "qlm_rth=True" -c {TCP_0[4]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-c-ms@1 --ofepisode 300 --aspid "1d-cont-ql-c-ms@1" -es 100 --prepfor "qlm_rth=True" -c {TCP_1[4]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@0 --ofepisode 300 --aspid "1d-cont-ql-p-ms@0" -es 100 --prepfor "qlm_rth=True" -c {HPP_0[4]}',
#     f'py .\pyrunner\model_extractor.py -pid ql-p-ms@1 --ofepisode 300 --aspid "1d-cont-ql-p-ms@1" -es 100 --prepfor "qlm_rth=True" -c {HPP_1[4]}',
# ]

################################################################################
# RUNNING BEST OF EACH GROUP, of 7 days, 3 days, 2 days, 1 day.
################################################################################

## TCP, Randomized Seed.
### To be run on 7 days, 3 days, 2 days, 1 day.

# commands = [
#     f'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@0 -alg lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -vc -c {TCP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {TCP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {TCP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {TCP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {TCP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 3d-cont-lfe-c-ms@0 -alg lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 2d-cont-lfe-c-ms@0 -alg lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 1d-cont-lfe-c-ms@0 -alg lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_0[4]}',
# # ]

## TCP, Fixed Seed.
### To be run on 7 days, 3 days, 2 days, 1 day.

# commands = [
#     f'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@1 -alg lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -vc -c {TCP_1[0]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {TCP_1[1]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {TCP_1[2]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {TCP_1[3]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {TCP_1[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 3d-cont-lfe-c-ms@1 -alg lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_1[0]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_1[1]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_1[2]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_1[3]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {TCP_1[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 2d-cont-lfe-c-ms@1 -alg lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_1[0]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_1[1]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_1[2]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_1[3]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {TCP_1[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 1d-cont-lfe-c-ms@1 -alg lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_1[0]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_1[1]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_1[2]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_1[3]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {TCP_1[4]}',
# # ]

## HPP, Randomized Seed.
### To be run on 7 days, 3 days, 2 days, 1 day.

# commands = [
#     f'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@0 -alg lfe-p-ms@0 -r 100 -mo "lfe_rth=True" -vc -c {HPP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {HPP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {HPP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {HPP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {HPP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 3d-cont-lfe-p-ms@0 -alg lfe-p-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 2d-cont-lfe-p-ms@0 -alg lfe-p-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 1d-cont-lfe-p-ms@0 -alg lfe-p-ms@0 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[4]}',
# # ]

## HPP, Fixed Seed.
### To be run on 7 days, 3 days, 2 days, 1 day.

# commands = [
#     f'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@1 -alg lfe-p-ms@1 -r 100 -mo "lfe_rth=True" -vc -c {HPP_1[0]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {HPP_1[1]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {HPP_1[2]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {HPP_1[3]}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {HPP_1[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 3d-cont-lfe-p-ms@1 -alg lfe-p-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 3d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=259200" -vc -c {HPP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 2d-cont-lfe-p-ms@1 -alg lfe-p-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 2d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=172800" -vc -c {HPP_0[4]}',
# # ]
# # commands = [
#     f'python pyrunner/batch_runner.py -pid 1d-cont-lfe-p-ms@1 -alg lfe-p-ms@1 -r 100 -mo "lfe_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[0]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[1]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[2]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[3]}',
#     f'python pyrunner/batch_runner.py -pid 1d-cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -po "Scenario.endTime=86400" -vc -c {HPP_0[4]}',
# # ]

"""
Simulations should be done now.
"""

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

### AFTER ABOVE, MERGE.

# ```sh
# python pyplotters/summary_merger.py -mf cont-lfe-c-ms@0 -mt cont-ql-c-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf cont-lfe-c-ms@1 -mt cont-ql-c-ms@1 --mvplots
# python pyplotters/summary_merger.py -mf cont-lfe-p-ms@0 -mt cont-ql-p-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf cont-lfe-p-ms@1 -mt cont-ql-p-ms@1 --mvplots
#
# ```

### THEN ANALYZE BEST PERFORMANCE PER GROUP.

# ```sh
# python pyplotters/bestof_plotter.py -pid cont-ql-c-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid cont-ql-c-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
# python pyplotters/bestof_plotter.py -pid cont-ql-p-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid cont-ql-p-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'
#
# ```

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

# ```sh
# python pyplotters/summary_merger.py -mf 1d-cont-lfe-c-ms@0 -mt 1d-cont-ql-c-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf 1d-cont-lfe-c-ms@1 -mt 1d-cont-ql-c-ms@1 --mvplots
# python pyplotters/summary_merger.py -mf 1d-cont-lfe-p-ms@0 -mt 1d-cont-ql-p-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf 1d-cont-lfe-p-ms@1 -mt 1d-cont-ql-p-ms@1 --mvplots
#
# ```

### THEN ANALYZE BEST PERFORMANCE PER GROUP.

# ```sh
# python pyplotters/bestof_plotter.py -pid 1d-cont-ql-c-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid 1d-cont-ql-c-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
# python pyplotters/bestof_plotter.py -pid 1d-cont-ql-p-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid 1d-cont-ql-p-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'
#
# ```

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

# ```sh
# python pyplotters/summary_merger.py -mf 2d-cont-lfe-c-ms@0 -mt 2d-cont-ql-c-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf 2d-cont-lfe-c-ms@1 -mt 2d-cont-ql-c-ms@1 --mvplots
# python pyplotters/summary_merger.py -mf 2d-cont-lfe-p-ms@0 -mt 2d-cont-ql-p-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf 2d-cont-lfe-p-ms@1 -mt 2d-cont-ql-p-ms@1 --mvplots
#
# ```

### THEN ANALYZE BEST PERFORMANCE PER GROUP.

# ```sh
# python pyplotters/bestof_plotter.py -pid 2d-cont-ql-c-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid 2d-cont-ql-c-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
# python pyplotters/bestof_plotter.py -pid 2d-cont-ql-p-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid 2d-cont-ql-p-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'
#
# ```

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

### AFTER ABOVE, MERGE

# ```sh
# python pyplotters/summary_merger.py -mf 3d-cont-lfe-c-ms@0 -mt 3d-cont-ql-c-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf 3d-cont-lfe-c-ms@1 -mt 3d-cont-ql-c-ms@1 --mvplots
# python pyplotters/summary_merger.py -mf 3d-cont-lfe-p-ms@0 -mt 3d-cont-ql-p-ms@0 --mvplots
# python pyplotters/summary_merger.py -mf 3d-cont-lfe-p-ms@1 -mt 3d-cont-ql-p-ms@1 --mvplots
#
# ```

### THEN ANALYZE BEST PERFORMANCE PER GROUP.

# ```sh
# python pyplotters/bestof_plotter.py -pid 3d-cont-ql-c-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid 3d-cont-ql-c-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
# python pyplotters/bestof_plotter.py -pid 3d-cont-ql-p-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
# python pyplotters/bestof_plotter.py -pid 3d-cont-ql-p-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'
#
# ```

################################################################################

# Placeholder command, comment this when using the program.
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
