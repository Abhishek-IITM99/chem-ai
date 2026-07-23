"""
make_charts.py
--------------
Render the deck charts from pipeline artifacts. Design follows the dataviz
method: form chosen by the data's job, validated blue/orange categorical pair
(blue = twin/optimized, orange = baseline), red reserved for labelled limit
lines, recessive grid, direct value labels, one y-axis per panel.

Outputs PNGs into ./artifacts for embedding in the Hub71 deck.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import joblib

from twin_pipeline import FEATURES, TARGET_LABELS

HERE = Path(__file__).parent
ART = HERE / "artifacts"

# palette (validated: #1D4ED8 / #EA580C pass all CVD checks on a light surface)
BLUE = "#1D4ED8"      # twin / optimized
ORANGE = "#EA580C"    # baseline / current
RED = "#B91C1C"       # limit lines (status, always labelled)
INK = "#1f2937"
MUTED = "#6b7280"
GRID = "#e5e7eb"
CARD = "#ffffff"

plt.rcParams.update({
    "figure.facecolor": CARD, "axes.facecolor": CARD,
    "savefig.facecolor": CARD, "font.size": 12, "text.color": INK,
    "axes.edgecolor": "#cbd5e1", "axes.labelcolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED,
    "font.family": "DejaVu Sans", "axes.titlesize": 13,
})


def _despine(ax):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)


def chart_accuracy(metrics):
    """Horizontal bars: R2 per target (magnitude comparison, one series)."""
    targets = metrics["targets"]
    r2 = [metrics["metrics"][t]["r2"] for t in targets]
    labels = [TARGET_LABELS[t] for t in targets]
    order = np.argsort(r2)
    r2 = np.array(r2)[order]
    labels = np.array(labels)[order]

    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=170)
    y = np.arange(len(r2))
    ax.barh(y, r2, color=BLUE, height=0.62, zorder=3)
    ax.set_yticks(y, labels)
    ax.set_xlim(0.9, 1.0)
    ax.set_xlabel("R² on 25 % hold-out test set")
    for yi, v in zip(y, r2):
        ax.text(v - 0.002, yi, f"{v:.3f}", va="center", ha="right",
                color="white", fontweight="bold", fontsize=11, zorder=4)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.set_title("Digital twin accuracy (R² on hold-out test set)",
                 fontweight="bold", loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(ART / "chart_accuracy.png")
    plt.close(fig)


def chart_realpred(preds_npz):
    """Real vs predicted scatter for efficiency (identity check)."""
    y = preds_npz["kpi_efficiency_pct_y"]
    yhat = preds_npz["kpi_efficiency_pct_yhat"]
    fig, ax = plt.subplots(figsize=(5.4, 5.0), dpi=170)
    lo, hi = min(y.min(), yhat.min()), max(y.max(), yhat.max())
    pad = (hi - lo) * 0.05
    ax.plot([lo - pad, hi + pad], [lo - pad, hi + pad], color=MUTED,
            linewidth=1.4, linestyle="--", zorder=2, label="perfect prediction")
    ax.scatter(y, yhat, s=16, color=BLUE, alpha=0.45, edgecolor="none", zorder=3)
    ax.set_xlim(lo - pad, hi + pad)
    ax.set_ylim(lo - pad, hi + pad)
    ax.set_xlabel("Actual efficiency (%)")
    ax.set_ylabel("Twin-predicted efficiency (%)")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    r2 = 1 - np.sum((y - yhat) ** 2) / np.sum((y - y.mean()) ** 2)
    ax.text(0.04, 0.94, f"R² = {r2:.3f}", transform=ax.transAxes,
            fontweight="bold", fontsize=13, color=INK, va="top")
    ax.legend(loc="lower right", frameon=False, fontsize=10)
    ax.set_title("Efficiency: twin vs truth", fontweight="bold",
                 loc="left", color=INK)
    fig.tight_layout()
    fig.savefig(ART / "chart_realpred.png")
    plt.close(fig)


def chart_sweep(opt):
    """Two stacked panels sharing x (excess air): efficiency, then CO.
    One y-axis per panel (never dual-axis). Baseline vs optimal marked."""
    sweep = pd.DataFrame(opt["sweep"])
    b = opt["baseline"]
    o = opt["optimized"]
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.2, 5.6), dpi=170,
                                   sharex=True, height_ratios=[3, 2])

    ax1.plot(sweep.excess_air_pct, sweep.efficiency_pct, color=INK,
             linewidth=2.2, zorder=3)
    ax1.scatter([b["excess_air_pct"]], [b["efficiency_pct"]], s=120,
                color=ORANGE, zorder=5, label="current operation")
    ax1.scatter([o["excess_air_pct"]], [o["efficiency_pct"]], s=120,
                color=BLUE, zorder=5, label="twin recommendation")
    ax1.annotate(f"{b['efficiency_pct']:.1f}%",
                 (b["excess_air_pct"], b["efficiency_pct"]),
                 textcoords="offset points", xytext=(6, -14), color=ORANGE,
                 fontweight="bold")
    ax1.annotate(f"{o['efficiency_pct']:.1f}%",
                 (o["excess_air_pct"], o["efficiency_pct"]),
                 textcoords="offset points", xytext=(6, 6), color=BLUE,
                 fontweight="bold")
    ax1.set_ylabel("Efficiency (%)")
    ax1.legend(loc="lower left", frameon=False, fontsize=10)
    _despine(ax1)
    ax1.set_title("Fuel efficiency vs excess air: the operating optimum",
                  fontweight="bold", loc="left", color=INK)

    ax2.plot(sweep.excess_air_pct, sweep.co_ppm, color=INK, linewidth=2.0,
             zorder=3)
    ax2.axhline(opt["assumptions"]["co_limit_ppm"], color=RED, linewidth=1.6,
                linestyle="--", zorder=2)
    ax2.text(sweep.excess_air_pct.max(), opt["assumptions"]["co_limit_ppm"],
             f"  CO limit {opt['assumptions']['co_limit_ppm']:.0f} ppm",
             color=RED, va="bottom", ha="right", fontsize=10, fontweight="bold")
    ax2.scatter([o["excess_air_pct"]], [o["co_ppm"]], s=90, color=BLUE, zorder=5)
    ax2.set_ylabel("CO (ppm)")
    ax2.set_xlabel("Excess air (%)")
    ax2.set_ylim(0, max(250, sweep.co_ppm.max() * 0.4))
    _despine(ax2)
    fig.tight_layout()
    fig.savefig(ART / "chart_sweep.png")
    plt.close(fig)


def chart_timeseries():
    """Actual vs twin-predicted efficiency over a window, faults shaded."""
    df = pd.read_csv(HERE / "heater_dataset.csv", parse_dates=["timestamp"])
    model = joblib.load(HERE / "models" / "twin_kpi_efficiency_pct.joblib")
    win = df.iloc[600:600 + 14 * 24].copy()          # 14-day window
    yhat = model.predict(win[FEATURES].values)

    fig, ax = plt.subplots(figsize=(7.4, 3.8), dpi=170)
    ax.plot(win.timestamp, win.kpi_efficiency_pct, color=ORANGE, linewidth=1.8,
            label="actual (first-principles)", zorder=3)
    ax.plot(win.timestamp, yhat, color=BLUE, linewidth=1.6, linestyle="--",
            label="twin prediction", zorder=4)
    # shade process-fault windows
    proc = win["fault_type"].isin(["air_deficiency", "high_excess_air",
                                   "fouling_spike", "fuel_upset"]).values
    t = win.timestamp.values
    in_span = False
    for i in range(len(proc)):
        if proc[i] and not in_span:
            start = t[i]; in_span = True
        if in_span and (i == len(proc) - 1 or not proc[i]):
            ax.axvspan(start, t[i], color="#fde68a", alpha=0.5, zorder=1)
            in_span = False
    _despine(ax)
    ax.set_ylabel("Efficiency (%)")
    ax.legend(loc="lower left", frameon=False, fontsize=10, ncol=2)
    ax.set_title("Twin vs actual efficiency (process faults shaded)",
                 fontweight="bold", loc="left", color=INK)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(ART / "chart_timeseries.png")
    plt.close(fig)


def main():
    metrics = json.loads((ART / "metrics.json").read_text())
    opt = json.loads((ART / "optimization.json").read_text())
    preds = np.load(ART / "test_predictions.npz")
    chart_accuracy(metrics)
    chart_realpred(preds)
    chart_sweep(opt)
    chart_timeseries()
    print("charts written to", ART)
    for p in sorted(ART.glob("chart_*.png")):
        print("  ", p.name, f"{p.stat().st_size//1024} KB")


if __name__ == "__main__":
    main()
