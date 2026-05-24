\usepackage{ulem}# 24-05-2026 Skripsi Data Processing Journal

## 1. Regarding results that are being used

I already had Lévy Flight reports dataset in stable episodes format, which consists of 750 episodes.
There is no need to reiterate the learning process.
Yesterday, I was re-running pid (environment) configurations of Posterior Sampling:

- `ql-c-ms@1`
- `ql-p-ms@0`
- `ql-p-ms@1`

Which had some issues with failing (reason: used a bugged onesim patch).
So I compiled the newer version and rerun the specific configurations (23-35) of all posterior sampling.

The runs have finished and all episodes seem to be stable and correct.
I have compressed them as a checkpoint folder.

## 2. Skripsi Latex (before any changes)

I reformatted some tables to be replaced with prettier left and right paddings.
The chapter 4 of hasil penelitian (Simulation Results) has also been updated by grouping each environment
into its each own subsubsection.

## 3. Changes to pesistence_plotter.py

I'm adding a "group" column after "configuration" column so that we can filter things out faster during
data processing.
And so, I reran all the persistence plotting from the reports to add that group column keying.

## 4. After rerunning persistence plots

I'm currently creating a spreadsheet sheet that will validate the plotters, by putting the summary.csv data
to cloud, I can transparently provide the source of my plotting.

It's done, can be accessed
in [Google Spreadsheets](https://docs.google.com/spreadsheets/d/11JAGernwg6I4VgUgClDjN8mzy-Om3hY07hGt-sdgFjU/edit?gid=1037889941#gid=1037889941).

## 5. Concluding Ranking

As we'll also evaluate how the "optimal" policies behave without learning process, I'll be running the
`model_extractor.py` for all the best performing algorithms aggregated by the `bestof_plotter.py`.

The current result of the best performers in each (ordered by rank) (
thanks: [tabletomarkdown](https://tabletomarkdown.com/convert-spreadsheet-to-markdown/):

### A. Thomas Clustering, Randomized Seed:

| rank | group      | cfg (index) | last_episode_cumulative_reward | Overridden Configuration Parameter Values        |
|------|------------|-------------|--------------------------------|--------------------------------------------------|
| 1    | ql_ps_gts  | 30          | 5281640                        | qlm_bp=ps, ps_iv=7.0                             |
| 2    | ql_ps_bbts | 35          | 4800940                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False  |
| 3    | ql_ucb     | 11          | 4769083                        | qlm_bp=ucb, ucb_ec=0.5                           |
| 4    | lf         | 36          | \-1018267                      | lfe_la=0.25                                      |
| 5    | ql_epsilon | 1           | \-1603452                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.99, eg_me=0.1 |

### B. Thomas Clustering, Fixed Seed:

| rank | group      | cfg (index) | last_episode_cumulative_reward | Overridden Configuration Parameter Values         |
|------|------------|-------------|--------------------------------|---------------------------------------------------|
| 1    | ql_ps_bbts | 35          | 4846920                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False   |
| 2    | ql_ucb     | 15          | 4746209                        | qlm_bp=ucb, ucb_ec=1.5                            |
| 3    | ql_ps_gts  | 23          | 4012503                        | qlm_bp=ps, ps_iv=0.5                              |
| 4    | lf         | 36          | \-979758                       | lfe_la=0.25                                       |
| 5    | ql_epsilon | 2           | \-1590949                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.991, eg_me=0.1 |

### C. Homogenous Poisson, Randomized Seed:

| rank | group      | cfg (index) | last_episode_cumulative_reward | Overridden Configuration Parameter Values        |
|------|------------|-------------|--------------------------------|--------------------------------------------------|
| 1    | ql_ps_gts  | 27          | 4943963                        | qlm_bp=ps, ps_iv=4.0                             |
| 2    | ql_ucb     | 14          | 4889212                        | qlm_bp=ucb, ucb_ec=1.25                          |
| 3    | ql_ps_bbts | 35          | 4816656                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False  |
| 4    | lf         | 36          | \-1039814                      | lfe_la=0.25                                      |
| 5    | ql_epsilon | 1           | \-1603806                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.99, eg_me=0.1 |

### D. Homogenous Poisson, Fixed Seed:

| rank | group      | cfg (index) | last_episode_cumulative_reward | Overridden Configuration Parameter Values        |
|------|------------|-------------|--------------------------------|--------------------------------------------------|
| 1    | ql_ucb     | 12          | 4853043                        | qlm_bp=ucb, ucb_ec=0.75                          |
| 2    | ql_ps_bbts | 35          | 4799657                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False  |
| 3    | ql_ps_gts  | 27          | 4504327                        | qlm_bp=ps, ps_iv=4.0                             |
| 4    | lf         | 36          | \-1048746                      | lfe_la=0.25                                      |
| 5    | ql_epsilon | 1           | \-1634916                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.99, eg_me=0.1 |

## 6. Runs to do (remotely)

As we'll also evaluate how the "optimal" policies behave without learning process, I'll be running the
`model_extractor.py` for all the best performing algorithms aggregated by the `bestof_plotter.py`.
This is ran to generate the average trajectory distribution.

### 7. Extract the best performing model weights

Using `model_extractor.py`, the following are the scripts used to sample the best, according to part 5 (results).
I also planned it whiffing 2 times with Claude, but it works now.

```shell
# Thomas Clustering, Randomized Seed (pid: best-ql-c-ms@0 and best-lfe-c-ms@0)
py .\pyrunner\model_extractor.py -pid ql-c-ms@0 -c 30,35,11,1 --ofepisode 750 --aspid "best-ql-c-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_pt=True,qlm_rth=True"
py .\pyrunner\model_extractor.py -pid lfe-c-ms@0 -c 36 --ofepisode 750 --aspid "best-lfe-c-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True"
# Thomas Clustering, Fixed Seed (pid: best-ql-c-ms@1 and best-lfe-c-ms@1)
py .\pyrunner\model_extractor.py -pid ql-c-ms@1 -c 35,15,23,2 --ofepisode 750 --aspid "best-ql-c-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_pt=True,qlm_rth=True"
py .\pyrunner\model_extractor.py -pid lfe-c-ms@1 -c 36 --ofepisode 750 --aspid "best-lfe-c-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True"
# Homogenous Poisson, Randomized Seed (pid: best-ql-p-ms@0 and best-lfe-p-ms@0)
py .\pyrunner\model_extractor.py -pid ql-p-ms@0 -c 27,14,35,1 --ofepisode 750 --aspid "best-ql-p-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_pt=True,qlm_rth=True"
py .\pyrunner\model_extractor.py -pid lfe-p-ms@0 -c 36 --ofepisode 750 --aspid "best-lfe-p-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True"
# Homogenous Poisson, Fixed Seed (pid: best-ql-p-ms@1 and best-lfe-p-ms@1)
py .\pyrunner\model_extractor.py -pid ql-p-ms@1 -c 12,35,27,1 --ofepisode 750 --aspid "best-ql-p-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_pt=True,qlm_rth=True"
py .\pyrunner\model_extractor.py -pid lfe-p-ms@1 -c 36 --ofepisode 750 --aspid "best-lfe-p-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True"

```

### 8. Running the best performing model weights

Then using the sampled model weights, we'll run 10 episodes.
We have to separate LF and QL runs because they run different algorithm settings base.
I had to update `QLearningMovement` becauase the previous implementation incorrectly pauses the MDP instead of the
update() invocation. It works now!

```shell
# Thomas Clustering, Randomized Seed (pid: best-ql-c-ms@0)
py .\pyrunner\batch_runner.py -pid best-ql-c-ms@0 -r 10 -c 30,35 -alg ql-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-ql-c-ms@0 -r 10 -c 11,1 -alg ql-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-lfe-c-ms@0 -r 10 -c 36 -alg lfe-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"
# Thomas Clustering, Fixed Seed (pid: best-ql-c-ms@1)
py .\pyrunner\batch_runner.py -pid best-ql-c-ms@1 -r 10 -c 35,15 -alg ql-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-ql-c-ms@1 -r 10 -c 23,2 -alg ql-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-lfe-c-ms@1 -r 10 -c 36 -alg lfe-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"
# Homogenous Poisson, Randomized Seed (pid: best-ql-p-ms@0)
py .\pyrunner\batch_runner.py -pid best-ql-p-ms@0 -r 10 -c 27,14 -alg ql-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-ql-p-ms@0 -r 10 -c 35,1 -alg ql-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-lfe-p-ms@0 -r 10 -c 36 -alg lfe-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"
# Homogenous Poisson, Fixed Seed (pid: best-ql-p-ms@1)
py .\pyrunner\batch_runner.py -pid best-ql-p-ms@1 -r 10 -c 12,35 -alg ql-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-ql-p-ms@1 -r 10 -c 27,1 -alg ql-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_pt=True,qlm_rth=True"
py .\pyrunner\batch_runner.py -pid best-lfe-p-ms@1 -r 10 -c 36 -alg lfe-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"

```

Okay running em all now.

### 9. Persistence Plotter on Best Performing Models

I've run all and the results are promising, now we'll plot each of the best performing models.

```shell
python pyplotters/persistence_plotter.py -pid best-lfe-c-ms@0 --title "Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid best-lfe-c-ms@1 --title "Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid best-lfe-p-ms@0 --title "Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid best-lfe-p-ms@1 --title "Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid best-ql-c-ms@0 --title "Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid best-ql-c-ms@1 --title "Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid best-ql-p-ms@0 --title "Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid best-ql-p-ms@1 --title "Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe

```

Now also running the Trajectory Distribution (aggregated) Plotter I just vibecoded.

```shell
python pyplotters/trajectory_aggregator.py -pid best-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid best-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid best-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/trajectory_aggregator.py -pid best-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe
python pyplotters/trajectory_aggregator.py -pid best-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid best-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid best-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/trajectory_aggregator.py -pid best-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe

```