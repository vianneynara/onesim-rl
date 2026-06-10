# PLOTTER SHEET

## Persistence Plotters

```sh
python pyplotters/persistence_plotter.py -pid lfe-c-ms@0 --title "Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-c-ms@1 --title "Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-p-ms@0 --title "Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-p-ms@1 --title "Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-c-ms@0 --title "Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-c-ms@1 --title "Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-p-ms@0 --title "Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-p-ms@1 --title "Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe

```

## Merging LFE run ids to QL

```sh
python pyplotters/summary_merger.py -mf lfe-c-ms@0 -mt ql-c-ms@0 --mvplots
python pyplotters/summary_merger.py -mf lfe-c-ms@1 -mt ql-c-ms@1 --mvplots
python pyplotters/summary_merger.py -mf lfe-p-ms@0 -mt ql-p-ms@0 --mvplots
python pyplotters/summary_merger.py -mf lfe-p-ms@1 -mt ql-p-ms@1 --mvplots

```

## Best of Plotters

### Levy Flight Episodic

```sh
python pyplotters/bestof_plotter.py -pid lfe-c-ms@0 --comparekey lfe_la --annotatediff
python pyplotters/bestof_plotter.py -pid lfe-c-ms@1 --comparekey lfe_la --annotatediff
python pyplotters/bestof_plotter.py -pid lfe-p-ms@0 --comparekey lfe_la --annotatediff
python pyplotters/bestof_plotter.py -pid lfe-p-ms@1 --comparekey lfe_la --annotatediff

```

### Q-Learning

Using classic qlm_bp (behavior policy)

```sh
python pyplotters/bestof_plotter.py -pid ql-c-ms@0 --comparekey qlm_bp --addparams qlm_bp@lfe --annotatediff --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-c-ms@1 --comparekey qlm_bp --addparams qlm_bp@lfe --annotatediff --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@0 --comparekey qlm_bp --addparams qlm_bp@lfe --annotatediff --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@1 --comparekey qlm_bp --addparams qlm_bp@lfe --annotatediff --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'

```

Using group-specific (cg@GROUP)

```sh
python pyplotters/bestof_plotter.py -pid ql-c-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-c-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'

```

## Best of Plotters Compare All

```sh
python pyplotters/bestof_plotter.py -pid ql-c-ms@0 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-c-ms@1 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@0 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@1 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'

```

## Best of Plotters Compare Per Group

```shell
# Thomas Clustered, Randomized Seed
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy\n$\\text{(Thomas Clustered, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound\n$\\text{(Thomas Clustered, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_ps_gts --title "Group Performance of Q-Learning with Gaussian Thompson Sampling\n$\\text{(Thomas Clustered, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_ps_bbts --title "Group Performance of Q-Learning with Beta-Binomial Thompson Sampling\n$\\text{(Thomas Clustered, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Thomas Clustered, Randomized Seed)}$"
# Thomas Clustered, Fixed Seed
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy\n$\\text{(Thomas Clustered, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound\n$\\text{(Thomas Clustered, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup ql_ps_gts --title "Group Performance of Q-Learning with Gaussian Thompson Sampling\n$\\text{(Thomas Clustered, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup ql_ps_bbts --title "Group Performance of Q-Learning with Beta-Binomial Thompson Sampling\n$\\text{(Thomas Clustered, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Thomas Clustered, Fixed Seed)}$"
# Homogenous-Poisson, Randomized Seed
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup ql_ps_gts --title "Group Performance of Q-Learning with Gaussian Thompson Sampling\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup ql_ps_bbts --title "Group Performance of Q-Learning with Beta-Binomial Thompson Sampling\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Homogenous-Poisson, Randomized Seed)}$"
# Homogenous-Poisson, Fixed Seed
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup ql_ps_gts --title "Group Performance of Q-Learning with Gaussian Thompson Sampling\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup ql_ps_bbts --title "Group Performance of Q-Learning with Beta-Binomial Thompson Sampling\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup lf --title "Group Performance of Lévy Flight\n$\\text{(Homogenous-Poisson, Fixed Seed)}$"

```

# How Plotter Works

## Persistence Plotter

### Overview

The Persistence Plotter transforms raw episode JSON data (from batch_runner output) into statistical visualizations and
aggregated CSV files. For each run, it:

- Extracts episode data from `ep/{episode_num}/Persistence-Episode@{episode_num}.json` files
- Generates per-episode time series plots: Cumulative Reward, Episode Reward, True Detections, Unique Detections,
  Trajectory Distribution (linear and log scale)
- Creates a `common_data.csv` file aggregating all episodes into a single dataframe for cross-episode analysis
- Generates a `summary.csv` (when processing all runs with `-pid`) capturing max rewards and detection counts per run
- Optionally adds run-id descriptions to plot titles using `-d, --describe`

This tool is a **prerequisite** for both best-of plotter and analysis workflows.

### Arguments

| Argument            | Type | Description                                                                                                                                           |
|---------------------|------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-pid, --parent_id` | str  | Process all run directories under `reports/skripsi/{all_of}/run-id/`. Generates summary.csv at output. Typical values: `ql`, `lfe`, `ql-c-ms@0`, etc. |
| `-rid, --run_id`    | str  | Process a single run directory by its identifier (searched recursively under `reports/skripsi/`). Use this to plot one specific run.                  |
| `-t, --title`       | str  | Custom title for all generated plots (e.g., "Q-Learning on Clustered Targets")                                                                        |
| `-d, --describe`    | flag | Parse run-id and append description to plot titles (e.g., adds `(movseed=0; learnseed=1)` for `ql-movseed@0-learnseed@1`)                             |

**Note**: Exactly one of `-pid` or `-rid` must be specified. Output plots are saved to
`pyplotters/plots/{aof or run_id}/`.

---

## Best-of Plotter

### Overview

The Best-of Plotter selects the best-performing run for each distinct group value and overlays their episode series on
shared comparison plots. It:

- Reads the `summary.csv` created by persistence_plotter (requires `-pid` to have been run first)
- Parses run-ids to extract key-value pairs (e.g., `ql-movseed@0-learnseed@1` → `{movseed: 0, learnseed: 1}`)
- Groups runs by a specified key (e.g., `qlm_bp` for behavior policy) and selects the run with highest
  `max_cumulative_reward` per group
- Creates overlay comparison plots: Episode Reward, Cumulative Reward, True Detections, Unique Detections
- Builds informative legend labels combining group value and override parameters

Useful for comparing algorithm variants or behavior policy effectiveness.

### Arguments

| Argument            | Type | Description                                                                                                                                                                                      |
|---------------------|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-pid, --parent_id` | str  | **Required.** Parent results directory under `pyplotters/plots/` (same value used in persistence_plotter `-pid`). Must already exist with `summary.csv`.                                         |
| `--comparekey`      | str  | **Required.** Grouping key for selecting best runs (e.g., `qlm_bp` groups by behavior policy, `qlm_ucb_ec` groups by UCB exploration constant). One best run per unique group value is selected. |
| `--addparams`       | str  | *(Optional)* Additional parameters to filter or annotate runs (not commonly used in current workflow)                                                                                            |
| `--title`           | str  | *(Optional)* Custom title for generated plots (e.g., "Behavior Policy Comparison")                                                                                                               |

**Dependencies**: Requires `{aof}/summary.csv` and `{aof}/{run_id}/common_data.csv` files to exist (generated by
persistence_plotter).

---

## Workflow Integration

1. **Batch Runner** → generates episode JSON in `reports/skripsi/{alg}/run-id/{config_id}/`
2. **Persistence Plotter** (with `-pid`) → reads all runs, generates plots and `summary.csv` in
   `pyplotters/plots/{aof}/`
3. **Best-of Plotter** → reads `summary.csv`, selects best per group, creates comparison plots

# Trajectory Aggregator

Useful to aggregate stable model's trajectory generation and visualize it as plots.
This script helps visualizing the trajectory distribution across episodes for a given run.

```shell
python pyplotters/persistence_plotter.py -pid lfe-c-ms@0 --title "Aggregated Trajectory Distribution" --describe
python pyplotters/persistence_plotter.py -pid lfe-c-ms@1 --title "Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-p-ms@0 --title "Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-p-ms@1 --title "Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-c-ms@0 --title "Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-c-ms@1 --title "Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-p-ms@0 --title "Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-p-ms@1 --title "Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe

```