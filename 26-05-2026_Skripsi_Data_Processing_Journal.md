# 26-05-2026 Skripsi Data Processing Journal

## 1. Using the last 100 episodes aggregated trajectory distribution for better visualization

Instead of a paused-training "stable" model, we should try running 100 episodes of the non-paused training.
This gives us learning summary from a newer 100 episodes.
We should extract the trained models in `cont-` prefixed folders.

### 1.1. Extracting the trained models

We extract the model weights from the last episode of initial training, and then prepare it with override param `*_rth=True`
so that it will reset the training history of the next runs.
We will also set the extracted model episode signature and episode count to 100.

```shell
# Thomas Clustering, Randomized Seed (pid: cont-ql-c-ms@0 and cont-lfe-c-ms@0)
py .\pyrunner\model_extractor.py -pid ql-c-ms@0 -c 30,35,11,1 --ofepisode 750 --aspid "cont-ql-c-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_rth=True" -es 100
py .\pyrunner\model_extractor.py -pid lfe-c-ms@0 -c 36 --ofepisode 750 --aspid "cont-lfe-c-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True" -es 100
# Thomas Clustering, Fixed Seed (pid: cont-ql-c-ms@1 and cont-lfe-c-ms@1)
py .\pyrunner\model_extractor.py -pid ql-c-ms@1 -c 35,15,23,2 --ofepisode 750 --aspid "cont-ql-c-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_rth=True" -es 100
py .\pyrunner\model_extractor.py -pid lfe-c-ms@1 -c 36 --ofepisode 750 --aspid "cont-lfe-c-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True" -es 100
# Homogenous Poisson, Randomized Seed (pid: cont-ql-p-ms@0 and cont-lfe-p-ms@0)
py .\pyrunner\model_extractor.py -pid ql-p-ms@0 -c 27,14,35,1 --ofepisode 750 --aspid "cont-ql-p-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_rth=True" -es 100
py .\pyrunner\model_extractor.py -pid lfe-p-ms@0 -c 36 --ofepisode 750 --aspid "cont-lfe-p-ms@0" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True" -es 100
# Homogenous Poisson, Fixed Seed (pid: cont-ql-p-ms@1 and cont-lfe-p-ms@1)
py .\pyrunner\model_extractor.py -pid ql-p-ms@1 -c 12,35,27,1 --ofepisode 750 --aspid "cont-ql-p-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "qlm_rth=True" -es 100
py .\pyrunner\model_extractor.py -pid lfe-p-ms@1 -c 36 --ofepisode 750 --aspid "cont-lfe-p-ms@1" -srp "D:\Developments+\Java\onesim-rl-data\reports" --prepfor "lfe_rth=True" -es 100

```

### 1.2. Running the extracted models for 100 episodes

```shell
# Thomas Clustering, Randomized Seed (pid: cont-ql-c-ms@0)
py .\pyrunner\batch_runner.py -pid cont-ql-c-ms@0 -r 100 -c 30,35 -alg ql-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-ql-c-ms@0 -r 100 -c 11,1 -alg ql-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-lfe-c-ms@0 -r 100 -c 36 -alg lfe-c-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"
# Thomas Clustering, Fixed Seed (pid: cont-ql-c-ms@1)
py .\pyrunner\batch_runner.py -pid cont-ql-c-ms@1 -r 100 -c 35,15 -alg ql-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-ql-c-ms@1 -r 100 -c 23,2 -alg ql-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-lfe-c-ms@1 -r 100 -c 36 -alg lfe-c-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"
# Homogenous Poisson, Randomized Seed (pid: cont-ql-p-ms@0)
py .\pyrunner\batch_runner.py -pid cont-ql-p-ms@0 -r 100 -c 27,14 -alg ql-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-ql-p-ms@0 -r 100 -c 35,1 -alg ql-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-lfe-p-ms@0 -r 100 -c 36 -alg lfe-p-ms@0 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"
# Homogenous Poisson, Fixed Seed (pid: cont-ql-p-ms@1)
py .\pyrunner\batch_runner.py -pid cont-ql-p-ms@1 -r 100 -c 12,35 -alg ql-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-ql-p-ms@1 -r 100 -c 27,1 -alg ql-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "qlm_rth=True"
py .\pyrunner\batch_runner.py -pid cont-lfe-p-ms@1 -r 100 -c 36 -alg lfe-p-ms@1 --setreportspath "D:\Developments+\Java\onesim-rl-data\reports" --continue -mo "lfe_rth=True"

```

### 1.3. Creating initial persistence plotting

```shell
python pyplotters/persistence_plotter.py -pid cont-lfe-c-ms@0 --title "Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid cont-lfe-c-ms@1 --title "Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid cont-lfe-p-ms@0 --title "Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid cont-lfe-p-ms@1 --title "Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid cont-ql-c-ms@0 --title "Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid cont-ql-c-ms@1 --title "Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/persistence_plotter.py -pid cont-ql-p-ms@0 --title "Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/persistence_plotter.py -pid cont-ql-p-ms@1 --title "Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe

```

### 1.4. Merging the persistence plots of LFE to QL

```shell
python pyplotters/summary_merger.py -mf cont-lfe-c-ms@0 -mt cont-ql-c-ms@0 --mvplots
python pyplotters/summary_merger.py -mf cont-lfe-c-ms@1 -mt cont-ql-c-ms@1 --mvplots
python pyplotters/summary_merger.py -mf cont-lfe-p-ms@0 -mt cont-ql-p-ms@0 --mvplots
python pyplotters/summary_merger.py -mf cont-lfe-p-ms@1 -mt cont-ql-p-ms@1 --mvplots

```

### 1.5. Graphic plotting of the persistence plots

```shell
python pyplotters/bestof_plotter.py -pid cont-ql-c-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid cont-ql-c-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Thomas Clustered, Fixed Seed)}$'
python pyplotters/bestof_plotter.py -pid cont-ql-p-ms@0 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Randomized Seed)}$'
python pyplotters/bestof_plotter.py -pid cont-ql-p-ms@1 --comparekey cg --addparams cg@other --title 'Best Performance Comparison of Lévy Flight vs Q-Learning\n$\\text{(Homogenous-Poisson, Fixed Seed)}$'

```

### 1.6. Aggregating the trajectory distribution

```shell
python pyplotters/trajectory_aggregator.py -pid cont-lfe-c-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid cont-lfe-c-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid cont-lfe-p-ms@0 --title "Aggregated Trajectory on Best Lévy Flight on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/trajectory_aggregator.py -pid cont-lfe-p-ms@1 --title "Aggregated Trajectory on Best Lévy Flight on Fixed Immobile Homogenous-Poisson Targets" --describe
python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets" --describe
python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@0 --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets" --describe
python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@1 --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets" --describe

```

### 1.7. Running the comparison trajectory distribution plotter

```shell
python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@0 --compareall --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Thomas Clustered Targets (100 eps)" --describe
python pyplotters/trajectory_aggregator.py -pid cont-ql-c-ms@1 --compareall --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Thomas Clustered Targets (100 eps)" --describe
python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@0 --compareall --title "Aggregated Trajectory on Best Q-Learning on Randomized Immobile Homogenous-Poisson Targets (100 eps)" --describe
python pyplotters/trajectory_aggregator.py -pid cont-ql-p-ms@1 --compareall --title "Aggregated Trajectory on Best Q-Learning on Fixed Immobile Homogenous-Poisson Targets (100 eps)" --describe

```