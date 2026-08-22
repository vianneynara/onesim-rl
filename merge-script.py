import subprocess
import os
from pathlib import Path

# Working directory - dynamically detect repo root where this script is located
WORK_DIR = Path(__file__).resolve().parent
VENV_ACTIVATE = WORK_DIR / ".venv" / "Scripts" / "activate.bat"

################################################################################
# THREE-WAY PIPELINE: mcn + ql + lfe combined, mirrors script-mix-initial.py
# stage-by-stage but every merge/compare step is done three-way instead of
# lfe-vs-ql only.
#
# HOW TO USE THIS FILE:
#   Every `commands = [...]` block below is commented out except the very
#   last one (`commands = []`, a no-op placeholder). To run a stage:
#     1. Comment out whichever `commands = [...]` was previously active.
#     2. Uncomment the ONE block for the stage you want to run.
#     3. Run this script. Wait for every opened cmd window to finish.
#     4. Move to the next stage and repeat.
#   Nothing needs to be hand-edited stage to stage - everything is already
#   filled in with real pids/titles/configs.
#
# STAGE ORDER:
#   1. Base simulations - initial persistence plotting        (12 commands)
#   2. Base simulations - initial trajectory aggregation       (12 commands)
#   3. Copy ql-* into new all-* folders (does NOT touch ql-*)    (4 commands)
#   4. Merge base runs three-way into all-* (lfe -> all, mcn -> all)
#                                                                 (8 commands)
#   5. Best-of compare-all on all-* (merged base runs)            (4 commands)
#   6. Trajectory compare-all on all-* (merged base runs)         (4 commands)
#   7. Extract best models + run cont- (7-day) simulations      (24 commands)
#   8. Cont- (7-day) plotting                                    (12 commands)
#   9. Cont- (7-day) trajectory aggregation                      (12 commands)
#  10. Copy cont-ql-* into new cont-all-* folders                 (4 commands)
#  11. Merge cont- (7-day) three-way into cont-all-*               (8 commands)
#  12. Cont- (7-day) best-of compare-all on cont-all-*             (4 commands)
#
# NOTE ON "all-*"/"cont-all-*": summary_merger.py requires --mergeto to
# already exist with a non-empty summary.csv, so a truly-empty new folder
# won't work as a merge target. Instead, Stage 3 (and Stage 10) makes a
# full copy of the ql-* / cont-ql-* directory under a new "all-*" /
# "cont-all-*" name first - that copy becomes the merge target, so the
# original lfe-*, ql-*, mcn-* (and cont- versions) directories are never
# written to or altered by any of this.
################################################################################

# commands = [
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-mcn-c-ms@0 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-mcn-c-ms@1 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-mcn-p-ms@0 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-mcn-p-ms@1 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-ql-c-ms@0 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-ql-c-ms@1 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-ql-p-ms@0 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-ql-p-ms@1 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-lfe-c-ms@0 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-lfe-c-ms@1 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-lfe-p-ms@0 --self-derive --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid 3d-cont-lfe-p-ms@1 --self-derive --replacegroup',
# ]

# commands = [
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-lfe-c-ms@0',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-lfe-c-ms@1',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-lfe-p-ms@0',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-lfe-p-ms@1',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-mcn-c-ms@0',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-mcn-c-ms@1',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-mcn-p-ms@0',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-mcn-p-ms@1',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-ql-c-ms@0',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-ql-c-ms@1',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-ql-p-ms@0',
#     r'python pyrunner/batch_shifter.py -pid 3d-cont-ql-p-ms@1',
# ]

## Best Configurations of Each Environment per Group
""" Index into each run's summary.csv rows (see -c flag), one per config bucket. """
LFE = [33]

QL_TCP_0 = [17, 23, 32]
QL_TCP_1 = [18, 22, 32]
QL_HPP_0 = [17, 24, 32]
QL_HPP_1 = [17, 22, 32]

MCN_TCP_0 = [4, 10, 16]
MCN_TCP_1 = [4, 12, 16]
# 4, 12, 18, 22, 32, 33
# 4, 12, 22, 27, 29, 33, 54
MCN_HPP_0 = [4, 12, 16]
MCN_HPP_1 = [4, 15, 16]

# Combined (lfe + ql + mcn) index lists, used for three-way --compareall -c
ALL_TCP_0 = LFE + QL_TCP_0 + MCN_TCP_0
ALL_TCP_1 = LFE + QL_TCP_1 + MCN_TCP_1
ALL_HPP_0 = LFE + QL_HPP_0 + MCN_HPP_0
ALL_HPP_1 = LFE + QL_HPP_1 + MCN_HPP_1

# ==============================================================================
# STAGE 1: BASE SIMULATIONS (300 EPISODES) - INITIAL PLOTTING
# ==============================================================================
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@0 --title "Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-c-ms@1 --title "Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@0 --title "Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid lfe-p-ms@1 --title "Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@0 --title "Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-c-ms@1 --title "Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@0 --title "Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid ql-p-ms@1 --title "Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid mcn-c-ms@0 --title "Monte Carlo Reinforcement Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid mcn-c-ms@1 --title "Monte Carlo Reinforcement Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid mcn-p-ms@0 --title "Monte Carlo Reinforcement Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid mcn-p-ms@1 --title "Monte Carlo Reinforcement Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# ==============================================================================
# STAGE 2: BASE SIMULATIONS - INITIAL TRAJECTORY AGGREGATOR
# ==============================================================================
# commands = [
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid mcn-c-ms@0 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid mcn-c-ms@1 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid mcn-p-ms@0 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -ule -pid mcn-p-ms@1 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# ==============================================================================
# STAGE 3: COPY ql-* INTO NEW all-* FOLDERS (ql-* itself is left untouched -
# this is what lets the merge target be a fresh folder instead of ql-*)
# ==============================================================================
# commands = [
#     r'xcopy "pyplotters\plots\mcn-c-ms@0" "pyplotters\plots\all-c-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\mcn-c-ms@1" "pyplotters\plots\all-c-ms@1" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\mcn-p-ms@0" "pyplotters\plots\all-p-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\mcn-p-ms@1" "pyplotters\plots\all-p-ms@1" /E /I /H /Y',
# ]

# ==============================================================================
# STAGE 4: MERGE BASE RUNS THREE-WAY INTO all-* (lfe -> all, mcn -> all),
# per environment. ql-*, lfe-*, mcn-* are only ever read from (-mf), never
# written to - only the all-* copy (-mt) gets modified.
# ==============================================================================
# commands = [
# #     r'python pyplotters/summary_merger.py -mf ql-c-ms@0 -mt all-c-ms@0 --mvplots',
# #     r'python pyplotters/summary_merger.py -mf ql-c-ms@1 -mt all-c-ms@1 --mvplots',
# #     r'python pyplotters/summary_merger.py -mf ql-p-ms@0 -mt all-p-ms@0 --mvplots',
# #     r'python pyplotters/summary_merger.py -mf ql-p-ms@1 -mt all-p-ms@1 --mvplots',
#
#     r'python pyplotters/summary_merger.py -mf lfe-c-ms@0 -mt all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf lfe-c-ms@1 -mt all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf lfe-p-ms@0 -mt all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf lfe-p-ms@1 -mt all-p-ms@1 --mvplots',
# ]

# ==============================================================================
# STAGE 5: BEST-OF COMPARE-ALL ON all-* (merged, ql-* untouched)
# ==============================================================================
# commands = [
#     r'python pyplotters/bestof_plotter.py -pid all-c-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid all-c-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Fixed Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid all-p-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid all-p-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"',
# ]

# ==============================================================================
# STAGE 6: TRAJECTORY COMPARE-ALL ON all-*, using the picked
# best-configuration indices (LFE + QL_* + MCN_* combined = ALL_*)
# ==============================================================================
# commands = [
#     f'python pyplotters/trajectory_aggregator.py -pid all-c-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid all-c-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Fixed Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid all-p-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid all-p-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Fixed Seed)" --describe',
# ]

# ==============================================================================
# STAGE 7: EXTRACT BEST MODELS + RUN cont- (7-DAY, 100 EPISODES) SIMULATIONS
# ==============================================================================
# commands = [
#     f'python pyrunner/model_extractor.py -pid lfe-c-ms@0 --ofepisode 300 --aspid "cont-lfe-c-ms@0" -es 100 --prepfor "lfe_rth=True" -c {",".join(map(str, LFE))}',
#     f'python pyrunner/model_extractor.py -pid lfe-c-ms@1 --ofepisode 300 --aspid "cont-lfe-c-ms@1" -es 100 --prepfor "lfe_rth=True" -c {",".join(map(str, LFE))}',
#     f'python pyrunner/model_extractor.py -pid lfe-p-ms@0 --ofepisode 300 --aspid "cont-lfe-p-ms@0" -es 100 --prepfor "lfe_rth=True" -c {",".join(map(str, LFE))}',
#     f'python pyrunner/model_extractor.py -pid lfe-p-ms@1 --ofepisode 300 --aspid "cont-lfe-p-ms@1" -es 100 --prepfor "lfe_rth=True" -c {",".join(map(str, LFE))}',
#
#     f'python pyrunner/model_extractor.py -pid ql-c-ms@0 --ofepisode 300 --aspid "cont-ql-c-ms@0" -es 100 --prepfor "qlm_rth=True" -c {",".join(map(str, QL_TCP_0))}',
#     f'python pyrunner/model_extractor.py -pid ql-c-ms@1 --ofepisode 300 --aspid "cont-ql-c-ms@1" -es 100 --prepfor "qlm_rth=True" -c {",".join(map(str, QL_TCP_1))}',
#     f'python pyrunner/model_extractor.py -pid ql-p-ms@0 --ofepisode 300 --aspid "cont-ql-p-ms@0" -es 100 --prepfor "qlm_rth=True" -c {",".join(map(str, QL_HPP_0))}',
#     f'python pyrunner/model_extractor.py -pid ql-p-ms@1 --ofepisode 300 --aspid "cont-ql-p-ms@1" -es 100 --prepfor "qlm_rth=True" -c {",".join(map(str, QL_HPP_1))}',
#
#     f'python pyrunner/model_extractor.py -pid mcn-c-ms@0 --ofepisode 300 --aspid "cont-mcn-c-ms@0" -es 100 --prepfor "mcnm_rth=True" -c {",".join(map(str, MCN_TCP_0))}',
#     f'python pyrunner/model_extractor.py -pid mcn-c-ms@1 --ofepisode 300 --aspid "cont-mcn-c-ms@1" -es 100 --prepfor "mcnm_rth=True" -c {",".join(map(str, MCN_TCP_1))}',
#     f'python pyrunner/model_extractor.py -pid mcn-p-ms@0 --ofepisode 300 --aspid "cont-mcn-p-ms@0" -es 100 --prepfor "mcnm_rth=True" -c {",".join(map(str, MCN_HPP_0))}',
#     f'python pyrunner/model_extractor.py -pid mcn-p-ms@1 --ofepisode 300 --aspid "cont-mcn-p-ms@1" -es 100 --prepfor "mcnm_rth=True" -c {",".join(map(str, MCN_HPP_1))}',
#
#     f'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@0 -alg lfe-c-ms@0 -r 100 -mo "lfe_rth=True" -vc -c {",".join(map(str, LFE))}',
#     f'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@1 -alg lfe-c-ms@1 -r 100 -mo "lfe_rth=True" -vc -c {",".join(map(str, LFE))}',
#     f'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@0 -alg lfe-p-ms@0 -r 100 -mo "lfe_rth=True" -vc -c {",".join(map(str, LFE))}',
#     f'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@1 -alg lfe-p-ms@1 -r 100 -mo "lfe_rth=True" -vc -c {",".join(map(str, LFE))}',
#
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@0 -alg ql-c-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {",".join(map(str, QL_TCP_0))}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-c-ms@1 -alg ql-c-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {",".join(map(str, QL_TCP_1))}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@0 -alg ql-p-ms@0 -r 100 -mo "qlm_rth=True" -vc -c {",".join(map(str, QL_HPP_0))}',
#     f'python pyrunner/batch_runner.py -pid cont-ql-p-ms@1 -alg ql-p-ms@1 -r 100 -mo "qlm_rth=True" -vc -c {",".join(map(str, QL_HPP_1))}',
#
#     f'python pyrunner/batch_runner.py -pid cont-mcn-c-ms@0 -alg mcn-c-ms@0 -r 100 -mo "mcnm_rth=True" -vc -c {",".join(map(str, MCN_TCP_0))}',
#     f'python pyrunner/batch_runner.py -pid cont-mcn-c-ms@1 -alg mcn-c-ms@1 -r 100 -mo "mcnm_rth=True" -vc -c {",".join(map(str, MCN_TCP_1))}',
#     f'python pyrunner/batch_runner.py -pid cont-mcn-p-ms@0 -alg mcn-p-ms@0 -r 100 -mo "mcnm_rth=True" -vc -c {",".join(map(str, MCN_HPP_0))}',
#     f'python pyrunner/batch_runner.py -pid cont-mcn-p-ms@1 -alg mcn-p-ms@1 -r 100 -mo "mcnm_rth=True" -vc -c {",".join(map(str, MCN_HPP_1))}',
# ]

# ==============================================================================
# STAGE 8: cont- (7-DAY) PLOTTING
# ==============================================================================
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-c-ms@0 --title "Best Performing Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-c-ms@1 --title "Best Performing Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-p-ms@0 --title "Best Performing Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-lfe-p-ms@1 --title "Best Performing Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-c-ms@0 --title "Best Performing Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-c-ms@1 --title "Best Performing Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-p-ms@0 --title "Best Performing Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-ql-p-ms@1 --title "Best Performing Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-mcn-c-ms@0 --title "Best Performing Monte Carlo Reinforcement Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-mcn-c-ms@1 --title "Best Performing Monte Carlo Reinforcement Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-mcn-p-ms@0 --title "Best Performing Monte Carlo Reinforcement Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid cont-mcn-p-ms@1 --title "Best Performing Monte Carlo Reinforcement Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# commands = [
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-c-ms@0 --title "Best Performing Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-c-ms@1 --title "Best Performing Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-p-ms@0 --title "Best Performing Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-p-ms@1 --title "Best Performing Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-c-ms@0 --title "Best Performing Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-c-ms@1 --title "Best Performing Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-p-ms@0 --title "Best Performing Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-ql-p-ms@1 --title "Best Performing Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-c-ms@0 --title "Best Performing Monte Carlo Reinforcement Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-c-ms@1 --title "Best Performing Monte Carlo Reinforcement Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-p-ms@0 --title "Best Performing Monte Carlo Reinforcement Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-p-ms@1 --title "Best Performing Monte Carlo Reinforcement Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# ==============================================================================
# STAGE 9: cont- (7-DAY) TRAJECTORY AGGREGATION
# ==============================================================================
# commands = [
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-mcn-c-ms@0 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-mcn-c-ms@1 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-mcn-p-ms@0 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid cont-mcn-p-ms@1 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# commands = [
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-c-ms@0 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-c-ms@1 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-p-ms@0 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-p-ms@1 --title "Aggregated Trajectory on Best Monte Carlo Reinforcement Learning on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# ==============================================================================
# STAGE 10: COPY cont-ql-* INTO NEW cont-all-* FOLDERS (cont-ql-* untouched)
# ==============================================================================
# commands = [
#     r'xcopy "pyplotters\plots\3d-cont-mcn-c-ms@0" "pyplotters\plots\3d-cont-all-c-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\3d-cont-mcn-c-ms@1" "pyplotters\plots\3d-cont-all-c-ms@1" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\3d-cont-mcn-p-ms@0" "pyplotters\plots\3d-cont-all-p-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\3d-cont-mcn-p-ms@1" "pyplotters\plots\3d-cont-all-p-ms@1" /E /I /H /Y',
#
#     r'xcopy "pyplotters\plots\2d-cont-mcn-c-ms@0" "pyplotters\plots\2d-cont-all-c-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\2d-cont-mcn-c-ms@1" "pyplotters\plots\2d-cont-all-c-ms@1" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\2d-cont-mcn-p-ms@0" "pyplotters\plots\2d-cont-all-p-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\2d-cont-mcn-p-ms@1" "pyplotters\plots\2d-cont-all-p-ms@1" /E /I /H /Y',

#     r'xcopy "pyplotters\plots\1d-cont-mcn-c-ms@0" "pyplotters\plots\1d-cont-all-c-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\1d-cont-mcn-c-ms@1" "pyplotters\plots\1d-cont-all-c-ms@1" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\1d-cont-mcn-p-ms@0" "pyplotters\plots\1d-cont-all-p-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\1d-cont-mcn-p-ms@1" "pyplotters\plots\1d-cont-all-p-ms@1" /E /I /H /Y',
#
#     r'xcopy "pyplotters\plots\cont-mcn-c-ms@0" "pyplotters\plots\cont-all-c-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\cont-mcn-c-ms@1" "pyplotters\plots\cont-all-c-ms@1" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\cont-mcn-p-ms@0" "pyplotters\plots\cont-all-p-ms@0" /E /I /H /Y',
#     r'xcopy "pyplotters\plots\cont-mcn-p-ms@1" "pyplotters\plots\cont-all-p-ms@1" /E /I /H /Y',
# ]

# ==============================================================================
# STAGE 11: cont- (7-DAY) MERGE THREE-WAY INTO cont-all- (lfe -> all, mcn -> all)
# ==============================================================================
# commands = [
#     r'python pyplotters/summary_merger.py -mf 3d-cont-ql-c-ms@0 -mt 3d-cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 3d-cont-ql-c-ms@1 -mt 3d-cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 3d-cont-ql-p-ms@0 -mt 3d-cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 3d-cont-ql-p-ms@1 -mt 3d-cont-all-p-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 3d-cont-lfe-c-ms@0 -mt 3d-cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 3d-cont-lfe-c-ms@1 -mt 3d-cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 3d-cont-lfe-p-ms@0 -mt 3d-cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 3d-cont-lfe-p-ms@1 -mt 3d-cont-all-p-ms@1 --mvplots',
# ]

# commands = [
#     r'python pyplotters/summary_merger.py -mf 2d-cont-ql-c-ms@0 -mt 2d-cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 2d-cont-ql-c-ms@1 -mt 2d-cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 2d-cont-ql-p-ms@0 -mt 2d-cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 2d-cont-ql-p-ms@1 -mt 2d-cont-all-p-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 2d-cont-lfe-c-ms@0 -mt 2d-cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 2d-cont-lfe-c-ms@1 -mt 2d-cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 2d-cont-lfe-p-ms@0 -mt 2d-cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 2d-cont-lfe-p-ms@1 -mt 2d-cont-all-p-ms@1 --mvplots',
# ]

# commands = [
#     r'python pyplotters/summary_merger.py -mf 1d-cont-ql-c-ms@0 -mt 1d-cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-ql-c-ms@1 -mt 1d-cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-ql-p-ms@0 -mt 1d-cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-ql-p-ms@1 -mt 1d-cont-all-p-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-c-ms@0 -mt 1d-cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-c-ms@1 -mt 1d-cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-p-ms@0 -mt 1d-cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-p-ms@1 -mt 1d-cont-all-p-ms@1 --mvplots',
# ]

# commands = [
#     r'python pyplotters/summary_merger.py -mf cont-ql-c-ms@0 -mt cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf cont-ql-c-ms@1 -mt cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf cont-ql-p-ms@0 -mt cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf cont-ql-p-ms@1 -mt cont-all-p-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf cont-lfe-c-ms@0 -mt cont-all-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf cont-lfe-c-ms@1 -mt cont-all-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf cont-lfe-p-ms@0 -mt cont-all-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf cont-lfe-p-ms@1 -mt cont-all-p-ms@1 --mvplots',
# ]

# ==============================================================================
# STAGE 12: cont- (7-DAY) BEST-OF COMPARE-ALL ON cont-all- (cont-ql- untouched)
# ==============================================================================
# commands = [
#     r'python pyplotters/bestof_plotter.py -pid 3d-cont-all-c-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 3d-cont-all-c-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Fixed Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 3d-cont-all-p-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 3d-cont-all-p-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"',
#
#     r'python pyplotters/bestof_plotter.py -pid 2d-cont-all-c-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 2d-cont-all-c-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Fixed Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 2d-cont-all-p-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 2d-cont-all-p-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"',

#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-all-c-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-all-c-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Fixed Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-all-p-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-all-p-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"',
#
#     r'python pyplotters/bestof_plotter.py -pid cont-all-c-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid cont-all-c-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Thomas Clustered, Fixed Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid cont-all-p-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid cont-all-p-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight, Q-Learning, and Monte Carlo\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"',
# ]

# commands = [
#     f'python pyplotters/trajectory_aggregator.py -pid 3d-cont-all-c-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 3d-cont-all-c-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Fixed Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 3d-cont-all-p-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 3d-cont-all-p-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Fixed Seed)" --describe',
#
#     f'python pyplotters/trajectory_aggregator.py -pid 2d-cont-all-c-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 2d-cont-all-c-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Fixed Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 2d-cont-all-p-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 2d-cont-all-p-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Fixed Seed)" --describe',

#     f'python pyplotters/trajectory_aggregator.py -pid 1d-cont-all-c-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 1d-cont-all-c-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Fixed Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 1d-cont-all-p-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid 1d-cont-all-p-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Fixed Seed)" --describe',
#
#     f'python pyplotters/trajectory_aggregator.py -pid cont-all-c-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid cont-all-c-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_TCP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Thomas Clustered, Fixed Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid cont-all-p-ms@0 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_0))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Randomized Seed)" --describe',
#     f'python pyplotters/trajectory_aggregator.py -pid cont-all-p-ms@1 --uselastepisode --compareall -c {",".join(map(str, ALL_HPP_1))} --title "Aggregated Trajectory Comparison: Lévy Flight vs Q-Learning vs Monte Carlo (Homogenous-Poisson, Fixed Seed)" --describe',
# ]

################################################################################
# Placeholder - keep this active when not running any stage.
################################################################################
# commands = []

# Open each command in a new Command Prompt window
for command in commands:
    full_cmd = (
        f'start "" cmd /k "cd /d \"{WORK_DIR}\" && '
        f'call \"{VENV_ACTIVATE}\" && '
        f'{command}"'
    )

    subprocess.Popen(full_cmd, shell=True)

print("Opened all command prompts.")