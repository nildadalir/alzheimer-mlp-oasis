# Python pipeline

End-to-end reproduction of the thesis experiment.

```bash
python -m pip install -r ../requirements.txt
python pipeline.py
```

The script:

1. Reads `data/raw/oasis_clinical.csv`
2. Drops Converted cases and encodes labels
3. Scales columns to `[-1, 1]`
4. Ranks features with MRMR
5. Makes a stratified 90/10 split (`random_state=42`)
6. Trains a tanh MLP with hidden layers `(8, 4)`
7. Evaluates three settings: all features, without eTIV/ASF, without CDR
8. Writes CSVs under `data/processed/` and figures under `results/`

The MLP is an `MLPRegressor` with a linear output that is thresholded at 0. That matches MATLAB `newff` (tansig hidden units, purelin output) more closely than `MLPClassifier`.
