"""Figure for the write-up: predicted vs true countdown, one panel per held-out clip."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e4e3df"
# Fixed categorical order: the color follows the model, whichever models are present.
SERIES = {"clock": "#2a78d6", "color": "#eb6834", "dinov2": "#1baf7a"}


def countdown_panels(predictions: pd.DataFrame, out_path: Path) -> Path:
    clips = list(dict.fromkeys(predictions.clip_id))
    models = [m for m in SERIES if m in set(predictions.model)]
    ncols = min(4, len(clips))
    nrows = -(-len(clips) // ncols)
    fig, axes = plt.subplots(nrows, ncols, figsize=(3.6 * ncols, 2.8 * nrows), squeeze=False)

    for ax, clip_id in zip(axes.flat, clips):
        d = predictions[predictions.clip_id == clip_id]
        truth = d[d.model == models[0]]
        ax.plot(truth.t, truth.tte_true, color=INK, lw=2, label="truth")
        for m in models:
            dm = d[d.model == m]
            ax.plot(dm.t, dm.tte_pred, color=SERIES[m], lw=1.5, label=m)
        ax.set_title(clip_id, fontsize=9, color=INK, loc="left")
        ax.set_ylim(bottom=0)
        ax.grid(color=GRID, lw=0.6)
        ax.tick_params(colors=MUTED, labelsize=8)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(GRID)
    for ax in list(axes.flat)[len(clips) :]:
        ax.set_visible(False)

    fig.supxlabel("time since start (s)", fontsize=9, color=MUTED)
    fig.supylabel("seconds until done", fontsize=9, color=MUTED)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper right", ncol=len(labels), frameon=False, fontsize=9)
    fig.suptitle("Countdown: predicted vs true", x=0.01, ha="left", fontsize=11, color=INK)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150, facecolor="#fcfcfb")
    plt.close(fig)
    return out_path
