# Thesis and README figures

Files in this folder are existing thesis assets, original MATLAB screenshots, or the pipeline diagram drawn from the documented method. They are not new experimental results.

## Experimental pipeline

| File | What it shows |
| --- | --- |
| `methodology_pipeline.png` | Steps used in this project: dataset → preprocessing → normalization → MRMR → 90/10 split → MLP → evaluation |
| `pipeline_overview.png` | Original thesis schematic (train/test partition and neural-network training) |

## Original MATLAB runs (2022)

Command-window listings from the submitted study. Test file size was 29 rows.

| File | What it shows |
| --- | --- |
| `matlab_run1.png` | Run printed 93.10% accuracy (9-8-4-1) |
| `matlab_run2.png` | Run printed 100% accuracy |
| `matlab_run3.png` | Run printed 100% accuracy |
| `matlab_run_reduced.png` | After dropping eTIV and ASF (7-8-4-1), printed 100% accuracy |
| `mrmr_scores.png` | MATLAB MRMR bar chart |
| `mrmr_values.png` | MATLAB MRMR numeric scores and rank indices |

Python reproduction plots (confusion matrices and the Python MRMR chart) live in [`../../results/`](../../results/).

## Background figures (thesis Chapters 1–2)

These illustrate the literature review. They are not outputs of the MLP.

`brain_comparison.png`, `mri_sample.jpeg`, `supervised_learning.png`, `neuron.png`, `random_forest.png`, `deep_network.png`, `elm.png`, `iau_logo.jpeg`
