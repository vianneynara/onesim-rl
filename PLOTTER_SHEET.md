# PLOTTER SHEET

## Persistence Plotters

```sh
python -m pythonplotters.persistence_plotter -aof lfe-p-ms@0 --title "Lévy Flight on Stochastic Stationary Poisson Distributed Targets" --describe
python -m pythonplotters.persistence_plotter -aof lfe-p-ms@1 --title "Lévy Flight on Fixed Stationary Poisson Distributed Targets" --describe
python -m pythonplotters.persistence_plotter -aof lfe-c-ms@0 --title "Lévy Flight on Stochastic Stationary Clustered Distributed Targets" --describe
python -m pythonplotters.persistence_plotter -aof lfe-c-ms@1 --title "Lévy Flight on Fixed Stationary Clustered Distributed Targets" --describe
python -m pythonplotters.persistence_plotter -aof ql-p-ms@0 --title "Q-Learning on Stochastic Stationary Poisson Distributed Targets" --describe
python -m pythonplotters.persistence_plotter -aof ql-p-ms@1 --title "Q-Learning on Fixed Stationary Poisson Distributed Targets" --describe
python -m pythonplotters.persistence_plotter -aof ql-c-ms@0 --title "Q-Learning on Stochastic Stationary Clustered Distributed Targets" --describe
python -m pythonplotters.persistence_plotter -aof ql-c-ms@1 --title "Q-Learning on Fixed Stationary Clustered Distributed Targets" --describe

```

## Best of Plotters

### Levy Flight Episodic

```sh
python -m pythonplotters.bestof_plotter -aof lfe-c-ms@0 --group lfe_la
python -m pythonplotters.bestof_plotter -aof lfe-c-ms@1 --group lfe_la
python -m pythonplotters.bestof_plotter -aof lfe-p-ms@0 --group lfe_la
python -m pythonplotters.bestof_plotter -aof lfe-p-ms@1 --group lfe_la

```

### Q-Learning

```sh
python -m pythonplotters.bestof_plotter -aof ql-c-ms@0 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"
python -m pythonplotters.bestof_plotter -aof ql-c-ms@1 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"
python -m pythonplotters.bestof_plotter -aof ql-p-ms@0 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"
python -m pythonplotters.bestof_plotter -aof ql-p-ms@1 --group qlm_bp --addparams qlm_bp@lfe --title "Lévy Flight vs Q-Learning with Behavior Policy Comparison"

```

## Merging LFE run ids to QL

```sh
python -m pythonplotters.summary_merger -mf lfe-c-ms@0 -mt ql-c-ms@0 -mvplot
python -m pythonplotters.summary_merger -mf lfe-c-ms@1 -mt ql-c-ms@1 -mvplot
python -m pythonplotters.summary_merger -mf lfe-p-ms@0 -mt ql-p-ms@0 -mvplot
python -m pythonplotters.summary_merger -mf lfe-p-ms@1 -mt ql-p-ms@1 -mvplot

```

# How Plotter Works