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
#     r'python pyrunner/batch_shifter.py -pid lfe-c-ms@0',
#     r'python pyrunner/batch_shifter.py -pid lfe-c-ms@1',
#     r'python pyrunner/batch_shifter.py -pid lfe-p-ms@0',
#     r'python pyrunner/batch_shifter.py -pid lfe-p-ms@1',
# ]

# # Commands to run (group_key_upgrader)
# commands = [
#     r'python pyrunner/group_key_upgrader.py -pid mcn-c-ms@0',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-c-ms@1',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-p-ms@0',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-p-ms@1',
# ]

# Commands to run (group_key_upgrader --replacegroup)
commands = [
#     r'python pyrunner/group_key_upgrader.py -pid mcn-c-ms@0 --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-c-ms@1 --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-p-ms@0 --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid mcn-p-ms@1 --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid cont-mcn-c-ms@0 --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid cont-mcn-c-ms@1 --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid cont-mcn-p-ms@0 --replacegroup',
#     r'python pyrunner/group_key_upgrader.py -pid cont-mcn-p-ms@1 --replacegroup',
]

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


# # Commands to run (batch running)
# # First Visit (fv=True)
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 1-8',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 1-8',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 9-17',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 9-17',
# ]
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 18-26',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 18-26',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 27-35',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 27-35',
# ]
#
# # Commands to run (batch running)
# # Every Visit (fv=False)
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 36-42',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 36-42',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 43-52',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 43-52',
# ]
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 53-61',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 53-61',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 62-70',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 62-70',
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
# commands = [
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 36-48,50,52 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 36-48,50,52 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 36-48,50,52 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 36-48,50,52 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@0 -alg mcn-c-ms@0 -c 54-70 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-c-ms@1 -alg mcn-c-ms@1 -c 54-70 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@0 -alg mcn-p-ms@0 -c 54-70 -vc',
#     r'python pyrunner/batch_runner.py -pid mcn-p-ms@1 -alg mcn-p-ms@1 -c 54-70 -vc',
# ]
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

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/persistence_plotter.py -pid mcn-c-ms@0 --title "Monte Carlo Reinforcement Learning on Stochastic Stationary Object Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid mcn-c-ms@1 --title "Monte Carlo Reinforcement Learning on Fixed Stationary Object Clustered Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid mcn-p-ms@0 --title "Monte Carlo Reinforcement Learning on Stochastic Stationary Object Poisson Distributed Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid mcn-p-ms@1 --title "Monte Carlo Reinforcement Learning on Fixed Stationary Object Poisson Distributed Targets" --describe',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/summary_merger.py -mf lfe-c-ms@0 -mt mcn-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf lfe-c-ms@1 -mt mcn-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf lfe-p-ms@0 -mt mcn-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf lfe-p-ms@1 -mt mcn-p-ms@1 --mvplots',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/bestof_plotter.py -pid mcn-c-ms@0 --comparekey cg --addparams cg@NA --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo Reinforcement Learning\n$\\text{(Clustered Distributed, Resampled Locations)}$"',
#     r'python pyplotters/bestof_plotter.py -pid mcn-c-ms@1 --comparekey cg --addparams cg@NA --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo Reinforcement Learning\n$\\text{(Clustered Distributed, Fixed Locations)}$"',
#     r'python pyplotters/bestof_plotter.py -pid mcn-p-ms@0 --comparekey cg --addparams cg@NA --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo Reinforcement Learning\n$\\text{(Poisson Distributed, Resampled Locations)}$"',
#     r'python pyplotters/bestof_plotter.py -pid mcn-p-ms@1 --comparekey cg --addparams cg@NA --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo Reinforcement Learning\n$\\text{(Poisson Distributed, Fixed Locations)}$"',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/bestof_plotter.py -pid mcn-c-ms@0 --compareall --title "Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Clustered Distributed, Resampled Locations)}$"',
#     r'python pyplotters/bestof_plotter.py -pid mcn-c-ms@1 --compareall --title "Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Clustered Distributed, Fixed Locations)}$"',
#     r'python pyplotters/bestof_plotter.py -pid mcn-p-ms@0 --compareall --title "Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Poisson Distributed, Resampled Locations)}$"',
#     r'python pyplotters/bestof_plotter.py -pid mcn-p-ms@1 --compareall --title "Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Poisson Distributed, Fixed Locations)}$"',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@0 --configgroup mcn_epsilon --title "Group Performance of Monte Carlo Reinforcement Learning with Epsilon Greedy\n$\\text{(Clustered Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@0 --configgroup mcn_ucb --title "Group Performance of Monte Carlo Reinforcement Learning with Upper Confidence Bound\n$\\text{(Clustered Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@0 --configgroup mcn_ps --title "Group Performance of Monte Carlo Reinforcement Learning with Posterior Sampling\n$\\text{(Clustered Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@0 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Clustered Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@1 --configgroup mcn_epsilon --title "Group Performance of Monte Carlo Reinforcement Learning with Epsilon Greedy\n$\\text{(Clustered Distributed, Fixed Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@1 --configgroup mcn_ucb --title "Group Performance of Monte Carlo Reinforcement Learning with Upper Confidence Bound\n$\\text{(Clustered Distributed, Fixed Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@1 --configgroup mcn_ps --title "Group Performance of Monte Carlo Reinforcement Learning with Posterior Sampling\n$\\text{(Clustered Distributed, Fixed Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-c-ms@1 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Clustered Distributed, Fixed Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@0 --configgroup mcn_epsilon --title "Group Performance of Monte Carlo Reinforcement Learning with Epsilon Greedy\n$\\text{(Poisson Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@0 --configgroup mcn_ucb --title "Group Performance of Monte Carlo Reinforcement Learning with Upper Confidence Bound\n$\\text{(Poisson Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@0 --configgroup mcn_ps --title "Group Performance of Monte Carlo Reinforcement Learning with Posterior Sampling\n$\\text{(Poisson Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@0 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Poisson Distributed, Resampled Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@1 --configgroup mcn_epsilon --title "Group Performance of Monte Carlo Reinforcement Learning with Epsilon Greedy\n$\\text{(Poisson Distributed, Fixed Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@1 --configgroup mcn_ucb --title "Group Performance of Monte Carlo Reinforcement Learning with Upper Confidence Bound\n$\\text{(Poisson Distributed, Fixed Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@1 --configgroup mcn_ps --title "Group Performance of Monte Carlo Reinforcement Learning with Posterior Sampling\n$\\text{(Poisson Distributed, Fixed Locations)}$"',
#     r'python -m pyplotters/bestof_plotter -pid mcn-p-ms@1 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Poisson Distributed, Fixed Locations)}$"',
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

# # Extract model
# # Commands to run, all base plotting
# commands = [
#     r'python pyrunner/model_extractor.py -pid mcn-c-ms@0 -c 70,51,66,44 --ofepisode 750 --aspid "cont-mcn-c-ms@0" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid mcn-c-ms@0 -c 12,8,30,34 --ofepisode 750 --aspid "cont-mcn-c-ms@0" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid lfe-c-ms@0 -c 71 --ofepisode 750 --aspid "cont-lfe-c-ms@0" --prepfor "lfe_rth=True" -es 100',
#
#     r'python pyrunner/model_extractor.py -pid mcn-c-ms@1 -c 70,52,67,23 --ofepisode 750 --aspid "cont-mcn-c-ms@1" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid mcn-c-ms@1 -c 13,44,8,34 --ofepisode 750 --aspid "cont-mcn-c-ms@1" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid lfe-c-ms@1 -c 71 --ofepisode 750 --aspid "cont-lfe-c-ms@1" --prepfor "lfe_rth=True" -es 100',
#
#     r'python pyrunner/model_extractor.py -pid mcn-p-ms@0 -c 70,56,67,29 --ofepisode 750 --aspid "cont-mcn-p-ms@0" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid mcn-p-ms@0 -c 20,44,9,34 --ofepisode 750 --aspid "cont-mcn-p-ms@0" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid lfe-p-ms@0 -c 71 --ofepisode 750 --aspid "cont-lfe-p-ms@0" --prepfor "lfe_rth=True" -es 100',
#
#     r'python pyrunner/model_extractor.py -pid mcn-p-ms@1 -c 70,51,65,24 --ofepisode 750 --aspid "cont-mcn-p-ms@1" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid mcn-p-ms@1 -c 21,44,8,35 --ofepisode 750 --aspid "cont-mcn-p-ms@1" --prepfor "mcnm_rth=True" -es 100',
#     r'python pyrunner/model_extractor.py -pid lfe-p-ms@1 -c 71 --ofepisode 750 --aspid "cont-lfe-p-ms@1" --prepfor "lfe_rth=True" -es 100',
# ]

# # Commands to run, all base plotting
# commands = [
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-c-ms@0 -r 100 -c 70,51,66,44 -alg mcn-c-ms@0 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-c-ms@0',
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-c-ms@0 -r 100 -c 12,8,30,34 -alg mcn-c-ms@0 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-c-ms@0',
# #     r'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@0 -r 100 -c 71 -alg lfe-c-ms@0 --continue -mo "lfe_rth=True" --aspid 1d-cont-lfe-c-ms@0',
#
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-c-ms@1 -r 100 -c 70,52,67,23 -alg mcn-c-ms@1 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-c-ms@1',
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-c-ms@1 -r 100 -c 13,44,8,34 -alg mcn-c-ms@1 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-c-ms@1',
# #     r'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@1 -r 100 -c 71 -alg lfe-c-ms@1 --continue -mo "lfe_rth=True" --aspid 1d-cont-lfe-c-ms@1',
#
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-p-ms@0 -r 100 -c 70,56,67,29 -alg mcn-p-ms@0 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-p-ms@0',
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-p-ms@0 -r 100 -c 20,44,9,34 -alg mcn-p-ms@0 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-p-ms@0',
# #     r'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@0 -r 100 -c 71 -alg lfe-p-ms@0 --continue -mo "lfe_rth=True" --aspid 1d-cont-lfe-p-ms@0',
#
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-p-ms@1 -r 100 -c 70,51,65,24 -alg mcn-p-ms@1 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-p-ms@1',
# #     r'python pyrunner/batch_runner.py -pid cont-mcn-p-ms@1 -r 100 -c 21,44,8,35 -alg mcn-p-ms@1 --continue -mo "mcnm_rth=True" --aspid 1d-cont-mcn-p-ms@1',
# #     r'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@1 -r 100 -c 71 -alg lfe-p-ms@1 --continue -mo "lfe_rth=True" --aspid 1d-cont-lfe-p-ms@1',
#
#     r'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@0 -r 100 -c 71 -alg lfe-c-ms@0 --continue -mo "lfe_rth=True" --aspid 3d-cont-lfe-c-ms@0',
#     r'python pyrunner/batch_runner.py -pid cont-lfe-c-ms@1 -r 100 -c 71 -alg lfe-c-ms@1 --continue -mo "lfe_rth=True" --aspid 3d-cont-lfe-c-ms@1',
#     r'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@0 -r 100 -c 71 -alg lfe-p-ms@0 --continue -mo "lfe_rth=True" --aspid 3d-cont-lfe-p-ms@0',
#     r'python pyrunner/batch_runner.py -pid cont-lfe-p-ms@1 -r 100 -c 71 -alg lfe-p-ms@1 --continue -mo "lfe_rth=True" --aspid 3d-cont-lfe-p-ms@1',
# ]

# # # Commands to run, all base plotting
# commands = [
# #     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-c-ms@0 --title "Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
# #     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-c-ms@1 --title "Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
# #     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-p-ms@0 --title "Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
# #     r'python pyplotters/persistence_plotter.py -pid 3d-cont-lfe-p-ms@1 --title "Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-c-ms@0 --title "Best Monte Carlo RL on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-c-ms@1 --title "Best Monte Carlo RL on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-p-ms@0 --title "Best Monte Carlo RL on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/persistence_plotter.py -pid 3d-cont-mcn-p-ms@1 --title "Best Monte Carlo RL on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-c-ms@0 -mt 1d-cont-mcn-c-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-c-ms@1 -mt 1d-cont-mcn-c-ms@1 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-p-ms@0 -mt 1d-cont-mcn-p-ms@0 --mvplots',
#     r'python pyplotters/summary_merger.py -mf 1d-cont-lfe-p-ms@1 -mt 1d-cont-mcn-p-ms@1 --mvplots',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-mcn-c-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo RL\n$\\text{(Thomas Clustered, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-mcn-c-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo RL\n$\\text{(Thomas Clustered, Fixed Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-mcn-p-ms@0 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo RL\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"',
#     r'python pyplotters/bestof_plotter.py -pid 1d-cont-mcn-p-ms@1 --comparekey cg --addparams cg@other --legend-outside --title "Best Performance Comparison of Lévy Flight vs Monte Carlo RL\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"',
# ]

# # Commands to run, all base plotting
# commands = [
# #     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe',
# #     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe',
# #     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe',
# #     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-mcn-c-ms@0 --title "Aggregated Trajectory on Best Monte Carlo RL on Randomized Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-mcn-c-ms@1 --title "Aggregated Trajectory on Best Monte Carlo RL on Fixed Immobile Thomas Clustered Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-mcn-p-ms@0 --title "Aggregated Trajectory on Best Monte Carlo RL on Randomized Immobile Homogenous-Poisson Targets" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 1d-cont-mcn-p-ms@1 --title "Aggregated Trajectory on Best Monte Carlo RL on Fixed Immobile Homogenous-Poisson Targets" --describe',
# ]

# # Commands to run, all base plotting
# commands = [
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-c-ms@0 --compareall --title "Aggregated Trajectory on Best Monte Carlo RL on Randomized Immobile Thomas Clustered Targets (100 eps)" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-c-ms@1 --compareall --title "Aggregated Trajectory on Best Monte Carlo RL on Fixed Immobile Thomas Clustered Targets (100 eps)" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-p-ms@0 --compareall --title "Aggregated Trajectory on Best Monte Carlo RL on Randomized Immobile Homogenous-Poisson Targets (100 eps)" --describe',
#     r'python pyplotters/trajectory_aggregator.py -pid 3d-cont-mcn-p-ms@1 --compareall --title "Aggregated Trajectory on Best Monte Carlo RL on Fixed Immobile Homogenous-Poisson Targets (100 eps)" --describe',
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