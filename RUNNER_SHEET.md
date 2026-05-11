# RUNNER SHEET

## Simulation runs with Batch Runner

### Running Epsilon Greedy Configs

```sh
python -m pyrunner.batch_runner -pid ql-c-ms@0 -c 1-6,31-38
python -m pyrunner.batch_runner -pid ql-c-ms@1 -c 1-6,31-38
python -m pyrunner.batch_runner -pid ql-p-ms@0 -c 1-6,31-38
python -m pyrunner.batch_runner -pid ql-p-ms@1 -c 1-6,31-38

```

### Running Upper Confidence Bound Configs

```sh
python -m pyrunner.batch_runner -pid ql-c-ms@0 -c 7-18
python -m pyrunner.batch_runner -pid ql-c-ms@1 -c 7-18
python -m pyrunner.batch_runner -pid ql-p-ms@0 -c 7-18
python -m pyrunner.batch_runner -pid ql-p-ms@1 -c 7-18

```

### Running Thompson Sampling Configs

```sh
python -m pyrunner.batch_runner -pid ql-c-ms@0 -c 19-22
python -m pyrunner.batch_runner -pid ql-c-ms@1 -c 19-22
python -m pyrunner.batch_runner -pid ql-p-ms@0 -c 19-22
python -m pyrunner.batch_runner -pid ql-p-ms@1 -c 19-22

```

### Running Lévy Flight Configs

```sh
python -m pyrunner.batch_runner -pid lfe-c-ms@0 -c 23-30
python -m pyrunner.batch_runner -pid lfe-c-ms@1 -c 23-30
python -m pyrunner.batch_runner -pid lfe-p-ms@0 -c 23-30
python -m pyrunner.batch_runner -pid lfe-p-ms@1 -c 23-30

```

# How Batch Runner

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

| Argument                | Type | Description                                                                                                      |
|-------------------------|------|------------------------------------------------------------------------------------------------------------------|
| `-c, --config`          | str  | Config index(es) to run. Supports single values (e.g., `1`), ranges (e.g., `1-6`), or mixed (e.g., `1-3,5,7-10`) |
| `-a, --all`             | flag | Run all configurations defined in `LIST_OF_CONFIGS` from `batch_configs.py`                                      |
| `-r, --runs`            | int  | Override number of episodes for all selected configs (if not set, uses config's `runs` value)                    |
| `-pid, --parent-dir-id` | str  | Custom name for report directory under `reports/skripsi/` (default: algorithm key like `ql`, `lfe`)              |
| `--verify`              | flag | Verify each config's episodes are complete and uncorrupted before running                                        |
| `--continue`            | flag | Verify and resume from last good episode by rebuilding `_persistence.json` from that episode                     |
| `-vc`                   | flag | Shortcut for `--verify --continue` combined                                                                      |
| `-cc, --count-configs`  | flag | Display total number of configs and exit (useful for checking config range limits)                               |

**Note**: `-c` and `-a` are mutually exclusive. If neither is specified, the runner shows help text.
