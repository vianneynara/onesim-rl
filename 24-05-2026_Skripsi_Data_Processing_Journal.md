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

1. Thomas Clustering, Randomized Seed:

| rank | group      | last_episode_cumulative_reward | Overridden Configuration Parameter Values        |
|------|------------|--------------------------------|--------------------------------------------------|
| 1    | ql_ps_gts  | 5281640                        | qlm_bp=ps, ps_iv=7.0                             |
| 2    | ql_ps_bbts | 4800940                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False  |
| 3    | ql_ucb     | 4769083                        | qlm_bp=ucb, ucb_ec=0.5                           |
| 4    | lf         | \-1018267                      | lfe_la=0.25                                      |
| 5    | ql_epsilon | \-1603452                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.99, eg_me=0.1 |

2. Thomas Clustering, Fixed Seed:

| rank | group      | last_episode_cumulative_reward | Overridden Configuration Parameter Values         |
|------|------------|--------------------------------|---------------------------------------------------|
| 1    | ql_ps_bbts | 4846920                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False   |
| 2    | ql_ucb     | 4746209                        | qlm_bp=ucb, ucb_ec=1.5                            |
| 3    | ql_ps_gts  | 4012503                        | qlm_bp=ps, ps_iv=0.5                              |
| 4    | lf         | \-979758                       | lfe_la=0.25                                       |
| 5    | ql_epsilon | \-1590949                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.991, eg_me=0.1 |

3. Homogenous Poisson, Randomized Seed:

| rank | group      | last_episode_cumulative_reward | Overridden Configuration Parameter Values        |
|------|------------|--------------------------------|--------------------------------------------------|
| 1    | ql_ps_gts  | 4943963                        | qlm_bp=ps, ps_iv=4.0                             |
| 2    | ql_ucb     | 4889212                        | qlm_bp=ucb, ucb_ec=1.25                          |
| 3    | ql_ps_bbts | 4816656                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False  |
| 4    | lf         | \-1039814                      | lfe_la=0.25                                      |
| 5    | ql_epsilon | \-1603806                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.99, eg_me=0.1 |

4. Homogenous Poisson, Fixed Seed:

| rank | group      | last_episode_cumulative_reward | Overridden Configuration Parameter Values        |
|------|------------|--------------------------------|--------------------------------------------------|
| 1    | ql_ucb     | 4853043                        | qlm_bp=ucb, ucb_ec=0.75                          |
| 2    | ql_ps_bbts | 4799657                        | qlm_bp=ps, ps_betabinomial=True, ps_reset=False  |
| 3    | ql_ps_gts  | 4504327                        | qlm_bp=ps, ps_iv=4.0                             |
| 4    | lf         | \-1048746                      | lfe_la=0.25                                      |
| 5    | ql_epsilon | \-1634916                      | qlm_bp=epsilon, eg_ip=1.0, eg_ed=0.99, eg_me=0.1 |


## 6. Runs to do (remotely)

As we'll also evaluate how the "optimal" policies behave without learning process, I'll be running the
`model_extractor.py` for all the best performing algorithms aggregated by the `bestof_plotter.py`.