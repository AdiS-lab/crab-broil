"""Clip labels and frame sampling.

A dataset is a CSV with one row per clip:

    clip_id,file,process,event_s,roi
    butter_01,data/clips/butter_01.mp4,browning,142.5,410,260,500,380

- ``file`` is relative to the CSV's directory (or absolute).
- ``event_s`` is the one hand label: seconds from the start of the video to the
  moment the process finishes (butter browns, water boils, ...). Every frame's
  target, the time left until that moment, follows from it.
- ``roi`` is optional ``x,y,w,h`` in source-video pixels around the pan. Leave it
  empty to use the whole frame.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

import cv2
import numpy as np

# Seconds of video kept after the event, so the model also sees what "done" looks like.
POST_EVENT_S = 10.0


@dataclass(frozen=True)
class Clip:
    clip_id: str
    path: Path
    process: str
    event_s: float
    roi: tuple[int, int, int, int] | None


def load_labels(csv_path: str | Path) -> list[Clip]:
    csv_path = Path(csv_path)
    clips = []
    with csv_path.open(newline="") as f:
        for row in csv.DictReader(f):
            roi_text = (row.get("roi") or "").strip()
            roi = tuple(int(v) for v in roi_text.split(",")) if roi_text else None
            if roi is not None and len(roi) != 4:
                raise ValueError(f"{row['clip_id']}: roi must be x,y,w,h, got {roi_text!r}")
            path = Path(row["file"])
            if not path.is_absolute():
                path = csv_path.parent / path
            clips.append(
                Clip(
                    clip_id=row["clip_id"].strip(),
                    path=path,
                    process=row["process"].strip(),
                    event_s=float(row["event_s"]),
                    roi=roi,
                )
            )
    if not clips:
        raise ValueError(f"{csv_path} has no clips")
    ids = [c.clip_id for c in clips]
    if len(set(ids)) != len(ids):
        raise ValueError(f"{csv_path} has duplicate clip_id values")
    return clips


def crop(frame: np.ndarray, roi: tuple[int, int, int, int] | None) -> np.ndarray:
    if roi is None:
        return frame
    x, y, w, h = roi
    return frame[y : y + h, x : x + w]


def sample_frames(clip: Clip, fps: float) -> Iterator[tuple[float, np.ndarray]]:
    """Yield ``(t_seconds, rgb_crop)`` at roughly ``fps`` until POST_EVENT_S after the event."""
    cap = cv2.VideoCapture(str(clip.path))
    if not cap.isOpened():
        raise FileNotFoundError(f"cannot open video {clip.path}")
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    stop_s = clip.event_s + POST_EVENT_S
    next_t = 0.0
    idx = 0
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            # Phone videos can have a variable frame rate, so prefer the container timestamp.
            pos_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            t = pos_ms / 1000.0 if pos_ms > 0 else idx / src_fps
            idx += 1
            if t > stop_s:
                break
            if t + 1e-6 < next_t:
                continue
            while next_t <= t + 1e-6:
                next_t += 1.0 / fps
            yield t, cv2.cvtColor(crop(frame, clip.roi), cv2.COLOR_BGR2RGB)
    finally:
        cap.release()
