# PLOTTER SHEET

## Persistence Plotters

```sh
python pyplotters/persistence_plotter.py -pid lfe-c-ms@0 --title "Lévy Flight on Stochastic Stationary Clustered Distributed Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-c-ms@1 --title "Lévy Flight on Fixed Stationary Clustered Distributed Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-p-ms@0 --title "Lévy Flight on Stochastic Stationary Poisson Distributed Targets" --describe
python pyplotters/persistence_plotter.py -pid lfe-p-ms@1 --title "Lévy Flight on Fixed Stationary Poisson Distributed Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-c-ms@0 --title "Q-Learning on Stochastic Stationary Clustered Distributed Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-c-ms@1 --title "Q-Learning on Fixed Stationary Clustered Distributed Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-p-ms@0 --title "Q-Learning on Stochastic Stationary Poisson Distributed Targets" --describe
python pyplotters/persistence_plotter.py -pid ql-p-ms@1 --title "Q-Learning on Fixed Stationary Poisson Distributed Targets" --describe

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
python pyplotters/bestof_plotter.py -pid lfe-c-ms@0 --group lfe_la
python pyplotters/bestof_plotter.py -pid lfe-c-ms@1 --group lfe_la
python pyplotters/bestof_plotter.py -pid lfe-p-ms@0 --group lfe_la
python pyplotters/bestof_plotter.py -pid lfe-p-ms@1 --group lfe_la

```

### Q-Learning

```sh
python pyplotters/bestof_plotter.py -pid ql-c-ms@0 --group qlm_bp --addparams qlm_bp@lfe --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Clustered Distributed, Resampled Locations)}$'
python pyplotters/bestof_plotter.py -pid ql-c-ms@1 --group qlm_bp --addparams qlm_bp@lfe --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Clustered Distributed, Fixed Locations)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@0 --group qlm_bp --addparams qlm_bp@lfe --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Poisson Distributed, Resampled Locations)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@1 --group qlm_bp --addparams qlm_bp@lfe --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Poisson Distributed, Fixed Locations)}$'

```

## Best of Plotters Compare All

```sh
python pyplotters/bestof_plotter.py -pid ql-c-ms@0 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Clustered Distributed, Resampled Locations)}$'
python pyplotters/bestof_plotter.py -pid ql-c-ms@1 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Clustered Distributed, Fixed Locations)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@0 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Poisson Distributed, Resampled Locations)}$'
python pyplotters/bestof_plotter.py -pid ql-p-ms@1 --compareall --title 'Bulk Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Poisson Distributed, Fixed Locations)}$'

```

## Best of Plotters Compare Per Group

```shell
# Clustered Distributed, Resampled Locations
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy (Clustered Distributed, Resampled Locations)"
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound (Clustered Distributed, Resampled Locations)"
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup ql_ts --title "Group Performance of Q-Learning with Posterior Sampling (Clustered Distributed, Resampled Locations)"
python -m pyplotters.bestof_plotter -pid ql-c-ms@0 --configgroup lf --title "Group Performance of Lévy Flight (Clustered Distributed, Resampled Locations)"
# Clustered Distributed, Fixed Locations
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy (Clustered Distributed, Fixed Locations)"
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound (Clustered Distributed, Fixed Locations)"
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup ql_ts --title "Group Performance of Q-Learning with Posterior Sampling (Clustered Distributed, Fixed Locations)"
python -m pyplotters.bestof_plotter -pid ql-c-ms@1 --configgroup lf --title "Group Performance of Lévy Flight (Clustered Distributed, Fixed Locations)"
# Poisson Distributed, Resampled Locations
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy (Poisson Distributed, Resampled Locations)"
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound (Poisson Distributed, Resampled Locations)"
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup ql_ts --title "Group Performance of Q-Learning with Posterior Sampling (Poisson Distributed, Resampled Locations)"
python -m pyplotters.bestof_plotter -pid ql-p-ms@0 --configgroup lf --title "Group Performance of Lévy Flight (Poisson Distributed, Resampled Locations)"
# Poisson Distributed, Fixed Locations
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup ql_epsilon --title "Group Performance of Q-Learning with Epsilon Greedy (Poisson Distributed, Fixed Locations)"
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup ql_ucb --title "Group Performance of Q-Learning with Upper Confidence Bound (Poisson Distributed, Fixed Locations)"
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup ql_ts --title "Group Performance of Q-Learning with Posterior Sampling (Poisson Distributed, Fixed Locations)"
python -m pyplotters.bestof_plotter -pid ql-p-ms@1 --configgroup lf --title "Group Performance of Lévy Flight (Poisson Distributed, Fixed Locations)"

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
| `--group`           | str  | **Required.** Grouping key for selecting best runs (e.g., `qlm_bp` groups by behavior policy, `qlm_ucb_ec` groups by UCB exploration constant). One best run per unique group value is selected. |
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
