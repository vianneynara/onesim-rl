# RUNNER SHEET

## Overall running with different ALG overriding

```sh
python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 1-35 -alg ql-c-ms@0
python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 1-35 -alg ql-c-ms@1
python pyrunner/batch_runner.py -pid ql-p-ms@0 -c 1-35 -alg ql-p-ms@0
python pyrunner/batch_runner.py -pid ql-p-ms@1 -c 1-35 -alg ql-p-ms@1
python pyrunner/batch_runner.py -pid lfe-c-ms@0 -c 36-43 -alg lfe-c-ms@0
python pyrunner/batch_runner.py -pid lfe-c-ms@1 -c 36-43 -alg lfe-c-ms@1
python pyrunner/batch_runner.py -pid lfe-p-ms@0 -c 36-43 -alg lfe-p-ms@0
python pyrunner/batch_runner.py -pid lfe-p-ms@1 -c 36-43 -alg lfe-p-ms@1

```

## Simulation runs with Batch Runner

### Running Epsilon Greedy Configs

```sh
python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 1-10
python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 1-10
python pyrunner/batch_runner.py -pid ql-p-ms@0 -c 1-10
python pyrunner/batch_runner.py -pid ql-p-ms@1 -c 1-10

```

### Running Upper Confidence Bound Configs

```sh
python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 11-22
python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 11-22
python pyrunner/batch_runner.py -pid ql-p-ms@0 -c 11-22
python pyrunner/batch_runner.py -pid ql-p-ms@1 -c 11-22

```

### Running Thompson Sampling Configs

```sh
python pyrunner/batch_runner.py -pid ql-c-ms@0 -c 23-35
python pyrunner/batch_runner.py -pid ql-c-ms@1 -c 23-35
python pyrunner/batch_runner.py -pid ql-p-ms@0 -c 23-35
python pyrunner/batch_runner.py -pid ql-p-ms@1 -c 23-35

```

### Running Lévy Flight Configs

```sh
python pyrunner/batch_runner.py -pid lfe-c-ms@0 -c 36-43
python pyrunner/batch_runner.py -pid lfe-c-ms@1 -c 36-43
python pyrunner/batch_runner.py -pid lfe-p-ms@0 -c 36-43
python pyrunner/batch_runner.py -pid lfe-p-ms@1 -c 36-43

```

# Episode Extender Module

This module provides a way to set up the existing run_id directories which already have alg+runs set with config_setting.json
containing respective `runner_id` and `runner_nrof_episodes`. As mixing this module into batch_runner will cause confusion of
goal, we separate it into a separate module.

```shell
py pyrunner\episode_extender.py -pid ql-c-ms@0 -fs ql500 --toepisodes 750 -c 1-35 --overwrite -ack
py pyrunner\episode_extender.py -pid ql-c-ms@1 -fs ql500 --toepisodes 750 -c 1-35 --overwrite -ack
py pyrunner\episode_extender.py -pid ql-p-ms@0 -fs ql500 --toepisodes 750 -c 1-35 --overwrite -ack
py pyrunner\episode_extender.py -pid ql-p-ms@1 -fs ql500 --toepisodes 750 -c 1-35 --overwrite -ack
py pyrunner\episode_extender.py -pid lfe-c-ms@0 -fs lfe500 --toepisodes 750 -c 36-43 --overwrite -ack
py pyrunner\episode_extender.py -pid lfe-c-ms@1 -fs lfe500 --toepisodes 750 -c 36-43 --overwrite -ack
py pyrunner\episode_extender.py -pid lfe-p-ms@0 -fs lfe500 --toepisodes 750 -c 36-43 --overwrite -ack
py pyrunner\episode_extender.py -pid lfe-p-ms@1 -fs lfe500 --toepisodes 750 -c 36-43 --overwrite -ack
```

# How Batch Runner Works

## Overview

The Batch Runner orchestrates episodic simulations for ONE-Sim reinforcement learning algorithms. It manages:

- **Algorithm selection**: Supports QL (Q-Learning), LFE (Lévy Flight Episodic), MC (Monte Carlo)
- **Configuration management**: Reads from `batch_configs.py` and applies indexed configurations
- **Behavior policies**: Optionally applies Epsilon-Greedy, Upper Confidence Bound (UCB), or Thompson Sampling (TS)
- **Override system**: Allows per-run parameter customization (learning rates, seeds, targets, etc.)
- **Episodic execution**: Runs multiple episodes sequentially via `one.bat`, persisting results to
  `reports/skripsi/{parent_dir_id}/run-id/{result_id_dir}`
- **Verification & recovery**: Can verify episode integrity and resume from the last successful episode

The runner generates:

- Episode JSON data in `ep/{episode_num}/` subdirectories
- Configuration summary in `config_setting.json`
- Main persistence file `_persistence.json` (rebuilt on recovery)

## Arguments

| Argument                | Type | Description                                                                                                                                                 |
|-------------------------|------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `-c, --config`          | str  | Config index(es) to run. Supports single values (e.g., `1`), ranges (e.g., `1-6`), or mixed (e.g., `1-3,5,7-10`)                                            |
| `-a, --all`             | flag | Run all configurations defined in `LIST_OF_CONFIGS` from `batch_configs.py`                                                                                 |
| `-r, --runs`            | int  | Override number of episodes for all selected configs (if not set, uses config's `runs` value)                                                               |
| `-pid, --parent-dir-id` | str  | Custom name for report directory under `reports/skripsi/` (default: algorithm key like `ql`, `lfe`)                                                         |
| `-alg`, `--algorithm`   | str  | Override algorithm config file using ALG_BASE_SETTINGS_PATH key (e.g., `ql`, `lfe`, `mc`). Lower priority than `--runcfg`                                   |
| `-rcfg` `--runcfg`      | str  | Override algorithm config file with custom config path (e.g., `custom-setting.cfg` or `settings/skripsi/custom-setting.cfg`). Takes precedence over `--alg` |
| `--verify`              | flag | Verify each config's episodes are complete and uncorrupted before running                                                                                   |
| `--continue`            | flag | Verify and resume from last good episode by rebuilding `_persistence.json` from that episode                                                                |
| `-vc`                   | flag | Shortcut for `--verify --continue` combined                                                                                                                 |
| `-cc, --count-configs`  | flag | Display total number of configs and exit (useful for checking config range limits)                                                                          |

**Note**: `-c` and `-a` are mutually exclusive. If neither is specified, the runner shows help text.
