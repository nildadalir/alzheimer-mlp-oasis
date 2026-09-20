# Python reproduction figures

Files in this folder are produced by `python/pipeline.py` (stratified 90/10 split, seed 42, 34 test records). They are not the original 2022 MATLAB screenshots.

| File | Content |
| --- | --- |
| `metrics.json` | Record counts, MRMR ranking, and MLP metrics for three settings |
| `mrmr_feature_importance.png` | Python MRMR ranking (CDR and MMSE highest) |
| `confusion_all_features.png` | Test-set confusion matrix, all 9 inputs |
| `confusion_reduced_features.png` | Same split after dropping eTIV and ASF |
| `confusion_without_cdr.png` | Same split with CDR withheld |

Original MATLAB screenshots and the thesis MRMR chart are in [`docs/figures/`](../docs/figures/).
