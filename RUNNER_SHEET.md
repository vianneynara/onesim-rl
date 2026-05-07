# RUNNER SHEET

## Simulation runs with Batch Runner

### Running Epsilon Greedy Configs

```sh
python -m pythonrunner.batch_runner -pid ql-p-ms@0 -c 1-6,31-38
python -m pythonrunner.batch_runner -pid ql-p-ms@1 -c 1-6,31-38
python -m pythonrunner.batch_runner -pid ql-c-ms@0 -c 1-6,31-38
python -m pythonrunner.batch_runner -pid ql-c-ms@1 -c 1-6,31-38

```

### Running Upper Confidence Bound Configs

```sh
python -m pythonrunner.batch_runner -pid ql-p-ms@0 -c 7-18
python -m pythonrunner.batch_runner -pid ql-p-ms@1 -c 7-18
python -m pythonrunner.batch_runner -pid ql-c-ms@0 -c 7-18
python -m pythonrunner.batch_runner -pid ql-c-ms@1 -c 7-18

```

### Running Thompson Sampling Configs

```sh
python -m pythonrunner.batch_runner -pid ql-p-ms@0 -c 19-22
python -m pythonrunner.batch_runner -pid ql-p-ms@1 -c 19-22
python -m pythonrunner.batch_runner -pid ql-c-ms@0 -c 19-22
python -m pythonrunner.batch_runner -pid ql-c-ms@1 -c 19-22

```

### Running Lévy Flight Configs

```sh
python -m pythonrunner.batch_runner -pid lfe-p-ms@0 -c 23-30
python -m pythonrunner.batch_runner -pid lfe-p-ms@1 -c 23-30
python -m pythonrunner.batch_runner -pid lfe-c-ms@0 -c 23-30
python -m pythonrunner.batch_runner -pid lfe-c-ms@1 -c 23-30

```

# How Batch Runner