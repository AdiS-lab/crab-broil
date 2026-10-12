"""Render the live-countdown demo video for one held-out clip.

The predictions come from ``evaluate`` (leave-one-clip-out), so the model never
saw this clip during training. Each video frame shows the latest prediction made
at or before that moment, i.e. what a live system would have shown.
"""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from .data import POST_EVENT_S, Clip


def _mmss(s: float) -> str:
    s = max(0, int(round(s)))
    return f"{s // 60}:{s % 60:02d}"


def _text(img, text, org, scale, color, thick):
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, (0, 0, 0), thick + 3, cv2.LINE_AA)
    cv2.putText(img, text, org, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def render(clip: Clip, predictions: pd.DataFrame, model: str, out_path: Path, max_width: int = 960) -> Path:
    d = predictions[(predictions.clip_id == clip.clip_id) & (predictions.model == model)].sort_values("t")
    if d.empty:
        raise SystemExit(f"no predictions for clip {clip.clip_id!r} and model {model!r}; run evaluate first")
    pt, pred = d.t.to_numpy(), d.tte_pred.to_numpy()

    cap = cv2.VideoCapture(str(clip.path))
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    w, h = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    scale = min(1.0, max_width / w) if w >= 640 else 640 / w  # small videos are upscaled so text stays readable
    size = (int(w * scale) // 2 * 2, int(h * scale) // 2 * 2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    writer = cv2.VideoWriter(str(out_path), cv2.VideoWriter_fourcc(*"mp4v"), src_fps, size)

    label = clip.process.upper()
    big = size[0] / 640
    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            pos_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            t = pos_ms / 1000.0 if pos_ms > 0 else idx / src_fps
            idx += 1
            if t > clip.event_s + POST_EVENT_S:
                break
            if clip.roi is not None:
                x, y, rw, rh = clip.roi
                cv2.rectangle(frame, (x, y), (x + rw, y + rh), (255, 255, 255), max(1, int(2 / scale)))
            frame = cv2.resize(frame, size, interpolation=cv2.INTER_AREA)

            i = int(np.searchsorted(pt, t, side="right")) - 1
            if i >= 0:
                # The prediction was made at pt[i]; it keeps ticking down until the next one.
                left = max(pred[i] - (t - pt[i]), 0.0)
                done = left <= 0.5
                color = (80, 80, 255) if left < 30 else (255, 255, 255)
                _text(frame, f"{label} {'NOW' if done else 'IN ' + _mmss(left)}", (int(20 * big), int(60 * big)), 1.4 * big, color, max(2, int(3 * big)))
            truth = max(clip.event_s - t, 0.0)
            _text(frame, f"actual: {_mmss(truth)}   model: {model}", (int(20 * big), size[1] - int(20 * big)), 0.75 * big, (235, 235, 235), 2)
            writer.write(frame)
    finally:
        cap.release()
        writer.release()
    return out_path
