# MATLAB pipeline

Corrected implementation of the bachelor-thesis experiments.

| Script | Purpose |
| --- | --- |
| `run_pipeline.m` | Runs the five steps below in order |
| `edit_dataset.m` | Drops Converted rows, encodes Group/Sex, fills missing SES/MMSE |
| `normalize.m` | Min–max scales every column to `[-1, 1]` |
| `feature_selection.m` | MRMR ranking via `fscmrmr` |
| `split_data.m` | True 90/10 split (`dividerand` with ratios `0.9, 0, 0.1`) |
| `mlp_classifier.m` | 9-8-4-1 feedforward net, standard TP/TN/FP/FN |

## Requirements

- MATLAB R2021a or newer (older releases may still run if `feedforwardnet` exists)
- Deep Learning Toolbox
- Statistics and Machine Learning Toolbox (only for `feature_selection.m`)

## Run

From this folder:

```matlab
run_pipeline
```

Or call a single step, for example:

```matlab
mlp_classifier
mlp_classifier('DropFeatures', [7 9])   % drop eTIV and ASF
```

Paths are resolved from the repository root, so the current working directory can be `matlab/`.

The original 2022 listings are kept under `../archive/matlab_original/` for comparison.
