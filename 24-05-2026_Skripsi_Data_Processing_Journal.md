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

### Extract the best performing model weights

Using `model_extractor.py`, the following are the scripts used to sample the best, according to part 5 (results).

```shell
# Thomas Clustering, Randomized Seed (pid: best-ql-c-ms@0 and best-lfe-c-ms@0)
py .\pyrunner\model_extractor.py -pid ql-c-ms@0 -c 30,35,11,36,1 --ofepisode 750 --aspid "best-ql-c-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports"
py .\pyrunner\model_extractor.py -pid lfe-c-ms@0 -c 36 --ofepisode 750 --aspid "best-lfe-c-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports"
# Thomas Clustering, Fixed Seed (pid: best-ql-c-ms@1 and best-lfe-c-ms@1)
py .\pyrunner\model_extractor.py -pid ql-c-ms@1 -c 35,15,23,36,2 --ofepisode 750 --aspid "best-ql-c-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports"
py .\pyrunner\model_extractor.py -pid lfe-c-ms@1 -c 36 --ofepisode 750 --aspid "best-lfe-c-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports"
# Homogenous Poisson, Randomized Seed (pid: best-ql-p-ms@0 and best-lfe-p-ms@0)
py .\pyrunner\model_extractor.py -pid ql-p-ms@0 -c 27,14,35,36,1 --ofepisode 750 --aspid "best-ql-p-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports"
py .\pyrunner\model_extractor.py -pid lfe-p-ms@0 -c 36 --ofepisode 750 --aspid "best-lfe-p-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports"
# Homogenous Poisson, Fixed Seed (pid: best-ql-p-ms@1 and best-lfe-p-ms@1)
py .\pyrunner\model_extractor.py -pid ql-p-ms@1 -c 12,35,27,36,1 --ofepisode 750 --aspid "best-ql-p-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports"
py .\pyrunner\model_extractor.py -pid lfe-p-ms@1 -c 36 --ofepisode 750 --aspid "best-lfe-p-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports"

```

### Running the best performing model weights

Then using the sampled model weights, we'll run 10 episodes.
We have to separate LF and QL runs because they run different algorithm settings base.

```shell
# Thomas Clustering, Randomized Seed (pid: best-ql-c-ms@0)
py .\pyrunner\batch_runner.py -pid best-ql-c-ms@0 -r 10 -c 30,35,11,1 -alg ql-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue
py .\pyrunner\batch_runner.py -pid best-lfe-c-ms@0 -r 10 -c 36 -alg lfe-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue
# Thomas Clustering, Fixed Seed (pid: best-ql-c-ms@1)
py .\pyrunner\batch_runner.py -pid best-ql-c-ms@1 -r 10 -c 35,15,23,2 -alg ql-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue
py .\pyrunner\batch_runner.py -pid best-lfe-c-ms@1 -r 10 -c 36 -alg lfe-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue
# Homogenous Poisson, Randomized Seed (pid: best-ql-p-ms@0)
py .\pyrunner\batch_runner.py -pid best-ql-p-ms@0 -r 10 -c 27,14,35,1 -alg ql-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue
py .\pyrunner\batch_runner.py -pid best-lfe-p-ms@0 -r 10 -c 36 -alg lfe-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue
# Homogenous Poisson, Fixed Seed (pid: best-ql-p-ms@1)
py .\pyrunner\batch_runner.py -pid best-ql-p-ms@1 -r 10 -c 12,35,27,1 -alg ql-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue
py .\pyrunner\batch_runner.py -pid best-lfe-p-ms@1 -r 10 -c 36 -alg lfe-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue

```