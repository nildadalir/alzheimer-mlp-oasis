"""
Alzheimer's disease detection from OASIS clinical features.

Reproduces the bachelor thesis pipeline:
  1. Drop Converted cases and encode Group / Sex
  2. Min-max normalize every column to [-1, 1]
  3. Rank features with MRMR
  4. 90/10 train-test split
  5. Train a 9-8-4-1 multilayer perceptron
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor

FEATURE_NAMES = ["Sex", "Age", "EDUC", "SES", "MMSE", "CDR", "eTIV", "nWBV", "ASF"]
ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "oasis_clinical.csv"
PROCESSED = ROOT / "data" / "processed"
RESULTS = ROOT / "results"
RANDOM_STATE = 42


def project_paths() -> tuple[Path, Path, Path]:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    return RAW_PATH, PROCESSED, RESULTS


def edit_dataset(raw_path: Path, out_path: Path) -> pd.DataFrame:
    df = pd.read_csv(raw_path)
    df = df[df["Group"].astype(str).str.strip().str.lower() != "converted"].copy()

    group_map = {"Demented": 1, "Nondemented": -1}
    sex_map = {"M": 1, "F": -1}
    df["Group"] = df["Group"].map(group_map)
    df["Sex"] = df["M/F"].map(sex_map)

    if df["Group"].isna().any() or df["Sex"].isna().any():
        raise ValueError("Unexpected Group or M/F labels after encoding.")

    # Match the original thesis: unknown SES -> 0, unknown MMSE -> 4
    df["SES"] = pd.to_numeric(df["SES"], errors="coerce").fillna(0)
    df["MMSE"] = pd.to_numeric(df["MMSE"], errors="coerce").fillna(4)

    edited = df[["Group", "Sex", "Age", "EDUC", "SES", "MMSE", "CDR", "eTIV", "nWBV", "ASF"]].astype(float)
    edited.to_csv(out_path, header=False, index=False)
    return edited


def normalize_minmax(data: np.ndarray, low: float = -1.0, high: float = 1.0) -> np.ndarray:
    col_min = data.min(axis=0)
    col_max = data.max(axis=0)
    span = np.where(col_max - col_min == 0, 1.0, col_max - col_min)
    scaled = (data - col_min) / span
    return (high - low) * scaled + low


def mrmr_rank(X: np.ndarray, y: np.ndarray) -> tuple[list[int], np.ndarray]:
    """Greedy MRMR using F-statistic relevance and |correlation| redundancy."""
    n_features = X.shape[1]
    relevance = _f_scores(X, y)

    selected: list[int] = []
    remaining = list(range(n_features))
    scores = np.zeros(n_features)

    first = int(np.argmax(relevance))
    selected.append(first)
    remaining.remove(first)
    scores[first] = relevance[first]

    while remaining:
        best_i = remaining[0]
        best_score = -np.inf
        for i in remaining:
            redundancy = np.mean([abs(_corr(X[:, i], X[:, j])) for j in selected])
            score = relevance[i] / (redundancy + 1e-12)
            if score > best_score:
                best_score = score
                best_i = i
        scores[best_i] = best_score
        selected.append(best_i)
        remaining.remove(best_i)

    return selected, scores


def _f_scores(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    classes = np.unique(y)
    scores = np.zeros(X.shape[1])
    for i in range(X.shape[1]):
        col = X[:, i]
        overall = col.mean()
        between = 0.0
        within = 0.0
        for c in classes:
            mask = y == c
            n_c = mask.sum()
            mu = col[mask].mean()
            between += n_c * (mu - overall) ** 2
            within += ((col[mask] - mu) ** 2).sum()
        df_b = len(classes) - 1
        df_w = max(len(col) - len(classes), 1)
        scores[i] = (between / df_b) / (within / df_w + 1e-12)
    return scores


def _corr(a: np.ndarray, b: np.ndarray) -> float:
    if np.std(a) == 0 or np.std(b) == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def metrics_from_labels(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    y_true_bin = (y_true == 1).astype(int)
    y_pred_bin = (y_pred == 1).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true_bin, y_pred_bin, labels=[0, 1]).ravel()
    return {
        "TP": int(tp),
        "TN": int(tn),
        "FP": int(fp),
        "FN": int(fn),
        "accuracy": float(accuracy_score(y_true_bin, y_pred_bin)),
        "precision": float(precision_score(y_true_bin, y_pred_bin, zero_division=0)),
        "recall": float(recall_score(y_true_bin, y_pred_bin, zero_division=0)),
        "specificity": float(tn / (tn + fp) if (tn + fp) else 0.0),
        "f1": float(f1_score(y_true_bin, y_pred_bin, zero_division=0)),
    }


def train_mlp(X_train: np.ndarray, y_train: np.ndarray, X_test: np.ndarray) -> tuple[np.ndarray, float, float]:
    """MATLAB newff used tansig hidden units and a linear output, then thresholded at 0."""
    model = MLPRegressor(
        hidden_layer_sizes=(8, 4),
        activation="tanh",
        solver="lbfgs",
        max_iter=2000,
        random_state=RANDOM_STATE,
    )
    t0 = time.perf_counter()
    model.fit(X_train, y_train)
    train_time = time.perf_counter() - t0

    t1 = time.perf_counter()
    scores = model.predict(X_test)
    pred = np.where(scores >= 0, 1, -1)
    test_time = time.perf_counter() - t1
    return pred, train_time, test_time


def plot_mrmr(idx: list[int], scores: np.ndarray, out_path: Path) -> None:
    ordered = scores[idx]
    labels = [FEATURE_NAMES[i] for i in idx]
    plt.figure(figsize=(8, 4.5))
    plt.bar(range(len(ordered)), ordered, color="#1f77b4")
    plt.xticks(range(len(ordered)), labels, rotation=45, ha="right")
    plt.xlabel("Predictor rank")
    plt.ylabel("Predictor importance score")
    plt.title("MRMR feature importance")
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def plot_confusion(metrics: dict[str, float], title: str, out_path: Path) -> None:
    matrix = np.array([[metrics["TN"], metrics["FP"]], [metrics["FN"], metrics["TP"]]])
    plt.figure(figsize=(4.6, 4.0))
    plt.imshow(matrix, cmap="Blues")
    plt.xticks([0, 1], ["Pred. healthy", "Pred. demented"])
    plt.yticks([0, 1], ["True healthy", "True demented"])
    for (i, j), value in np.ndenumerate(matrix):
        plt.text(j, i, int(value), ha="center", va="center", fontsize=14)
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def run(seed: int = RANDOM_STATE) -> dict:
    raw_path, processed, results = project_paths()
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw dataset not found: {raw_path}")

    edited = edit_dataset(raw_path, processed / "dataset2_edited.csv")
    data = edited.to_numpy(dtype=float)
    normalized = normalize_minmax(data)
    np.savetxt(processed / "dataset3_normalized.csv", normalized, delimiter=",", fmt="%.10g")

    y = normalized[:, 0]
    X = normalized[:, 1:]
    idx, scores = mrmr_rank(X, y)
    plot_mrmr(idx, scores, results / "mrmr_feature_importance.png")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.10, random_state=seed, stratify=y
    )
    np.savetxt(
        processed / "dataset4_train.csv",
        np.column_stack([y_train, X_train]),
        delimiter=",",
        fmt="%.10g",
    )
    np.savetxt(
        processed / "dataset5_test.csv",
        np.column_stack([y_test, X_test]),
        delimiter=",",
        fmt="%.10g",
    )

    pred_all, train_t, test_t = train_mlp(X_train, y_train, X_test)
    metrics_all = metrics_from_labels(y_test, pred_all)
    metrics_all.update({"train_time_s": train_t, "test_time_s": test_t, "n_features": int(X.shape[1])})
    plot_confusion(metrics_all, "MLP — all features", results / "confusion_all_features.png")

    keep = [i for i, name in enumerate(FEATURE_NAMES) if name not in {"eTIV", "ASF"}]
    pred_red, train_t_r, test_t_r = train_mlp(X_train[:, keep], y_train, X_test[:, keep])
    metrics_red = metrics_from_labels(y_test, pred_red)
    metrics_red.update({"train_time_s": train_t_r, "test_time_s": test_t_r, "n_features": len(keep)})
    plot_confusion(metrics_red, "MLP — without eTIV & ASF", results / "confusion_reduced_features.png")

    # Honest ablation: CDR is almost a clinical diagnosis, not an independent biomarker
    keep_no_cdr = [i for i, name in enumerate(FEATURE_NAMES) if name != "CDR"]
    pred_no_cdr, _, _ = train_mlp(X_train[:, keep_no_cdr], y_train, X_test[:, keep_no_cdr])
    metrics_no_cdr = metrics_from_labels(y_test, pred_no_cdr)
    metrics_no_cdr["n_features"] = len(keep_no_cdr)
    plot_confusion(metrics_no_cdr, "MLP — without CDR", results / "confusion_without_cdr.png")

    summary = {
        "n_records_original": int(pd.read_csv(raw_path).shape[0]),
        "n_records_used": int(len(edited)),
        "class_counts": {
            "Demented": int((edited["Group"] == 1).sum()),
            "Nondemented": int((edited["Group"] == -1).sum()),
        },
        "mrmr_ranking": [
            {"rank": rank + 1, "feature": FEATURE_NAMES[i], "score": float(scores[i])}
            for rank, i in enumerate(idx)
        ],
        "mlp_all_features": metrics_all,
        "mlp_without_etiv_asf": metrics_red,
        "mlp_without_cdr": metrics_no_cdr,
        "split": {"train": int(len(y_train)), "test": int(len(y_test)), "seed": seed},
    }
    (results / "metrics.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def _print_metrics(title: str, m: dict) -> None:
    print(f"\n{title}")
    print(f"  TP={m['TP']}  TN={m['TN']}  FP={m['FP']}  FN={m['FN']}")
    print(f"  accuracy={m['accuracy']:.4f}  precision={m['precision']:.4f}  "
          f"recall={m['recall']:.4f}  f1={m['f1']:.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Alzheimer MLP pipeline")
    parser.add_argument("--seed", type=int, default=RANDOM_STATE)
    args = parser.parse_args()

    summary = run(seed=args.seed)
    print(f"Used {summary['n_records_used']} records "
          f"({summary['class_counts']['Demented']} demented, "
          f"{summary['class_counts']['Nondemented']} nondemented).")
    print("MRMR ranking:", ", ".join(item["feature"] for item in summary["mrmr_ranking"]))
    _print_metrics("MLP — all 9 features", summary["mlp_all_features"])
    _print_metrics("MLP — without eTIV & ASF", summary["mlp_without_etiv_asf"])
    _print_metrics("MLP — without CDR (ablation)", summary["mlp_without_cdr"])
    print(f"\nWrote metrics and figures to {RESULTS}")


if __name__ == "__main__":
    main()
