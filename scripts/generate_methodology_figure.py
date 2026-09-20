"""Draw the documented experimental pipeline for the README (no new claims)."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures" / "methodology_pipeline.png"

STEPS = [
    "OASIS clinical table\n373 records",
    "Preprocessing\nDrop Converted · encode Group / Sex\nFill missing SES / MMSE  →  336 records",
    "Min–max normalization\nto [−1, +1]",
    "MRMR feature ranking",
    "Train / test split\n90% / 10%",
    "Multilayer perceptron\n9–8–4–1",
    "Evaluation\nAccuracy, precision, recall, F1, TP / TN / FP / FN",
]


def rounded_box(ax, x, y, w, h, text, facecolor, edgecolor, fontsize=10.5):
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2),
        w,
        h,
        boxstyle="round,pad=0.018,rounding_size=0.08",
        linewidth=1.4,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize, color="#1b2a4a", linespacing=1.35)


def main() -> None:
    n = len(STEPS)
    fig_h = 11.2
    fig, ax = plt.subplots(figsize=(7.2, fig_h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")
    ax.set_title(
        "Experimental pipeline",
        fontsize=14,
        color="#1b2a4a",
        pad=8,
        fontweight="bold",
    )

    top, bottom = 0.935, 0.055
    span = top - bottom
    ys = [top - i * span / (n - 1) for i in range(n)]
    width, height = 0.78, 0.105
    face = "#eef4fb"
    edge = "#2f5d8a"

    for i, (y, text) in enumerate(zip(ys, STEPS)):
        rounded_box(ax, 0.5, y, width, height, text, face, edge)
        if i < n - 1:
            y0 = y - height / 2 - 0.004
            y1 = ys[i + 1] + height / 2 + 0.004
            ax.add_patch(
                FancyArrowPatch(
                    (0.5, y0),
                    (0.5, y1),
                    arrowstyle="-|>",
                    mutation_scale=12,
                    linewidth=1.3,
                    color=edge,
                    shrinkA=0,
                    shrinkB=0,
                )
            )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT, dpi=160, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
