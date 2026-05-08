# PLOTTER SHEET

## Persistence Plotters

```sh
python -m pyplotters.persistence_plotter -aof lfe-c-ms@0 --title "Lévy Flight on Stochastic Stationary Clustered Distributed Targets" --describe
python -m pyplotters.persistence_plotter -aof lfe-c-ms@1 --title "Lévy Flight on Fixed Stationary Clustered Distributed Targets" --describe
python -m pyplotters.persistence_plotter -aof lfe-p-ms@0 --title "Lévy Flight on Stochastic Stationary Poisson Distributed Targets" --describe
python -m pyplotters.persistence_plotter -aof lfe-p-ms@1 --title "Lévy Flight on Fixed Stationary Poisson Distributed Targets" --describe
python -m pyplotters.persistence_plotter -aof ql-c-ms@0 --title "Q-Learning on Stochastic Stationary Clustered Distributed Targets" --describe
python -m pyplotters.persistence_plotter -aof ql-c-ms@1 --title "Q-Learning on Fixed Stationary Clustered Distributed Targets" --describe
python -m pyplotters.persistence_plotter -aof ql-p-ms@0 --title "Q-Learning on Stochastic Stationary Poisson Distributed Targets" --describe
python -m pyplotters.persistence_plotter -aof ql-p-ms@1 --title "Q-Learning on Fixed Stationary Poisson Distributed Targets" --describe

```

## Best of Plotters

### Levy Flight Episodic

```sh
python -m pyplotters.bestof_plotter -aof lfe-c-ms@0 --group lfe_la
python -m pyplotters.bestof_plotter -aof lfe-c-ms@1 --group lfe_la
python -m pyplotters.bestof_plotter -aof lfe-p-ms@0 --group lfe_la
python -m pyplotters.bestof_plotter -aof lfe-p-ms@1 --group lfe_la

```

### Q-Learning

```sh
python -m pyplotters.bestof_plotter -aof ql-c-ms@0 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"
python -m pyplotters.bestof_plotter -aof ql-c-ms@1 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"
python -m pyplotters.bestof_plotter -aof ql-p-ms@0 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"
python -m pyplotters.bestof_plotter -aof ql-p-ms@1 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"

```

## Merging LFE run ids to QL

```sh
python -m pyplotters.summary_merger -mf lfe-c-ms@0 -mt ql-c-ms@0 -mvplot
python -m pyplotters.summary_merger -mf lfe-c-ms@1 -mt ql-c-ms@1 -mvplot
python -m pyplotters.summary_merger -mf lfe-p-ms@0 -mt ql-p-ms@0 -mvplot
python -m pyplotters.summary_merger -mf lfe-p-ms@1 -mt ql-p-ms@1 -mvplot

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
- Generates a `summary.csv` (when processing all runs with `-aof`) capturing max rewards and detection counts per run
- Optionally adds run-id descriptions to plot titles using `-d, --describe`

This tool is a **prerequisite** for both best-of plotter and analysis workflows.

### Arguments

| Argument         | Type | Description                                                                                                                                           |
|------------------|------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-aof, --all_of` | str  | Process all run directories under `reports/skripsi/{all_of}/run-id/`. Generates summary.csv at output. Typical values: `ql`, `lfe`, `ql-c-ms@0`, etc. |
| `-rid, --run_id` | str  | Process a single run directory by its identifier (searched recursively under `reports/skripsi/`). Use this to plot one specific run.                  |
| `-t, --title`    | str  | Custom title for all generated plots (e.g., "Q-Learning on Clustered Targets")                                                                        |
| `-d, --describe` | flag | Parse run-id and append description to plot titles (e.g., adds `(movseed=0; learnseed=1)` for `ql-movseed@0-learnseed@1`)                             |

**Note**: Exactly one of `-aof` or `-rid` must be specified. Output plots are saved to
`pyplotters/plots/{aof or run_id}/`.

---

## Best-of Plotter

### Overview

The Best-of Plotter selects the best-performing run for each distinct group value and overlays their episode series on
shared comparison plots. It:

- Reads the `summary.csv` created by persistence_plotter (requires `-aof` to have been run first)
- Parses run-ids to extract key-value pairs (e.g., `ql-movseed@0-learnseed@1` → `{movseed: 0, learnseed: 1}`)
- Groups runs by a specified key (e.g., `qlm_bp` for behavior policy) and selects the run with highest
  `max_cumulative_reward` per group
- Creates overlay comparison plots: Episode Reward, Cumulative Reward, True Detections, Unique Detections
- Builds informative legend labels combining group value and override parameters

Useful for comparing algorithm variants or behavior policy effectiveness.

### Arguments

| Argument         | Type | Description                                                                                                                                                                                      |
|------------------|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-aof, --all_of` | str  | **Required.** Parent results directory under `pyplotters/plots/` (same value used in persistence_plotter `-aof`). Must already exist with `summary.csv`.                                         |
| `--group`        | str  | **Required.** Grouping key for selecting best runs (e.g., `qlm_bp` groups by behavior policy, `qlm_ucb_ec` groups by UCB exploration constant). One best run per unique group value is selected. |
| `--addparams`    | str  | *(Optional)* Additional parameters to filter or annotate runs (not commonly used in current workflow)                                                                                            |
| `--title`        | str  | *(Optional)* Custom title for generated plots (e.g., "Behavior Policy Comparison")                                                                                                               |

**Dependencies**: Requires `{aof}/summary.csv` and `{aof}/{run_id}/common_data.csv` files to exist (generated by
persistence_plotter).

---

## Workflow Integration

1. **Batch Runner** → generates episode JSON in `reports/skripsi/{alg}/run-id/{config_id}/`
2. **Persistence Plotter** (with `-aof`) → reads all runs, generates plots and `summary.csv` in
   `pyplotters/plots/{aof}/`
3. **Best-of Plotter** → reads `summary.csv`, selects best per group, creates comparison plots
