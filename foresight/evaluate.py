"""Leave-one-clip-out training and evaluation.

For each clip: train every model on the other clips (same process when there is
another clip of that process, otherwise all other clips), predict the held-out
clip frame by frame, and score the countdown against the hand label.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .data import Clip
from .features import clip_features
from .models import ClockBaseline, VisionRegressor, smooth_countdown, time_to_event

# How close the countdown has to be to count as "locked on".
LOCK_TOL_S = 10.0


def model_names(backends: list[str]) -> list[str]:
    names = ["clock"]
    for b in backends:
        names += [b, f"{b}+clock"]
    return names


def lock_seconds(tte: np.ndarray, pred: np.ndarray, tol: float) -> float:
    """For how many seconds before the event is the countdown within ±tol without a miss?"""
    order = np.argsort(tte)
    ok = np.abs(pred[order] - tte[order]) <= tol
    if ok.all():
        return float(tte[order][-1])
    first_miss = int(np.argmin(ok))
    return 0.0 if first_miss == 0 else float(tte[order][first_miss - 1])


def score(tte: np.ndarray, pred: np.ndarray, tol: float) -> dict[str, float]:
    err = np.abs(pred - tte)
    near = tte <= 60
    return {
        "mae_s": float(err.mean()),
        "mae_last60_s": float(err[near].mean()) if near.any() else np.nan,
        "lock_s": lock_seconds(tte, pred, tol),
    }


def training_set(held: Clip, clips: list[Clip], pool: bool) -> tuple[list[Clip], str]:
    others = [c for c in clips if c.clip_id != held.clip_id]
    same = [c for c in others if c.process == held.process]
    if same and not pool:
        return same, "same-process"
    return others, "pooled"


def run(
    clips: list[Clip],
    backends: list[str],
    fps: float,
    cache_dir: Path,
    out_dir: Path,
    pool: bool = False,
    tol: float = LOCK_TOL_S,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    if len(clips) < 2:
        raise SystemExit("need at least 2 labelled clips for leave-one-clip-out")

    feats = {(b, c.clip_id): clip_features(c, b, fps, cache_dir) for b in backends for c in clips}
    time_axis = {c.clip_id: feats[(backends[0], c.clip_id)][0] for c in clips}

    metric_rows, pred_rows = [], []
    for held in clips:
        train, train_mode = training_set(held, clips, pool)
        t = time_axis[held.clip_id]
        tte = time_to_event(t, held.event_s)
        preds = {"clock": ClockBaseline().fit([c.event_s for c in train]).predict(t)}
        for b in backends:
            data = [(*feats[(b, c.clip_id)], c.event_s) for c in train]
            for use_clock in (False, True):
                model = VisionRegressor(b, use_clock).fit(data)
                preds[model.name] = model.predict(*feats[(b, held.clip_id)])

        scored = t <= held.event_s  # after the event the answer is trivially 0
        for name, raw in preds.items():
            pred = smooth_countdown(t, raw)
            metric_rows.append(
                {
                    "clip_id": held.clip_id,
                    "process": held.process,
                    "event_s": held.event_s,
                    "train": f"{train_mode} ({len(train)} clips)",
                    "model": name,
                    **score(tte[scored], pred[scored], tol),
                }
            )
            pred_rows.append(
                pd.DataFrame(
                    {"clip_id": held.clip_id, "model": name, "t": t, "tte_true": tte, "tte_pred": pred}
                )
            )

    metrics = pd.DataFrame(metric_rows)
    predictions = pd.concat(pred_rows, ignore_index=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(out_dir / "metrics_per_clip.csv", index=False)
    predictions.to_csv(out_dir / "predictions.csv", index=False)
    write_summary(metrics, model_names(backends), out_dir, tol)
    return metrics, predictions


def write_summary(metrics: pd.DataFrame, order: list[str], out_dir: Path, tol: float) -> pd.DataFrame:
    summary = (
        metrics.groupby("model")[["mae_s", "mae_last60_s", "lock_s"]]
        .mean()
        .reindex([m for m in order if m in set(metrics.model)])
    )
    clock_mae = metrics[metrics.model == "clock"].set_index("clip_id").mae_s
    beats = metrics.assign(beats=lambda d: d.mae_s < d.clip_id.map(clock_mae)).groupby("model").beats.sum()
    n = metrics.clip_id.nunique()
    summary["clips_beating_clock"] = [f"{int(beats[m])}/{n}" if m != "clock" else "-" for m in summary.index]
    summary.to_csv(out_dir / "summary.csv")

    lines = [
        f"Leave-one-clip-out over {n} clips. Lower error is better; higher lock is better.",
        "",
        f"| model | error, all frames (s) | error, last 60 s (s) | locked within ±{tol:g} s for final (s) | clips beating clock |",
        "|---|---|---|---|---|",
    ]
    for m, r in summary.iterrows():
        lines.append(
            f"| {m} | {r.mae_s:.1f} | {r.mae_last60_s:.1f} | {r.lock_s:.1f} | {r.clips_beating_clock} |"
        )
    (out_dir / "summary.md").write_text("\n".join(lines) + "\n")
    return summary
