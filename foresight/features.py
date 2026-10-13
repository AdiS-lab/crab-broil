"""Per-frame visual features, cached to ``cache/features/<backend>/<clip_id>.npz``.

Backends:

- ``color``: hand-crafted color, texture and motion statistics of the pan region.
  No downloads, runs anywhere. This is the "simple pixels" baseline.
- ``dinov2``: the CLS embedding of a frozen, pretrained DINOv2 encoder
  (``facebook/dinov2-small`` by default). Needs the ``deep`` extra and downloads
  weights from huggingface.co the first time.

Features never include the timestamp. Elapsed time only enters through the
explicit ``clock`` baseline and the ``+clock`` model variants.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import cv2
import numpy as np

from .data import Clip, sample_frames

BACKENDS = ("color", "dinov2")
DINOV2_MODEL = "facebook/dinov2-small"


def color_features(rgb: np.ndarray, prev_gray: np.ndarray | None) -> tuple[np.ndarray, np.ndarray]:
    """26 numbers describing color, texture and motion. Returns ``(features, gray)``."""
    small = cv2.resize(rgb, (96, 96), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(small, cv2.COLOR_RGB2LAB).reshape(-1, 3).astype(np.float32)
    hsv = cv2.cvtColor(small, cv2.COLOR_RGB2HSV).reshape(-1, 3).astype(np.float32)
    gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY).astype(np.float32)

    hue_hist = np.histogram(hsv[:, 0], bins=8, range=(0, 180), weights=hsv[:, 1] + 1)[0]
    val_hist = np.histogram(hsv[:, 2], bins=4, range=(0, 256))[0]
    texture = np.abs(cv2.Laplacian(gray, cv2.CV_32F)).mean()  # bubbles, crisping edges
    motion = 0.0 if prev_gray is None else float(np.abs(gray - prev_gray).mean())  # boiling, sizzling

    feats = np.concatenate(
        [
            lab.mean(0),
            lab.std(0),
            hsv.mean(0),
            hsv.std(0),
            hue_hist / hue_hist.sum(),
            val_hist / val_hist.sum(),
            [texture, motion],
        ]
    )
    return feats.astype(np.float32), gray


def _color_clip(clip: Clip, fps: float) -> tuple[np.ndarray, np.ndarray]:
    ts, rows, prev = [], [], None
    for t, rgb in sample_frames(clip, fps):
        feats, prev = color_features(rgb, prev)
        ts.append(t)
        rows.append(feats)
    return np.array(ts), np.stack(rows)


def _load_dinov2(name: str):
    try:
        import torch
        from transformers import AutoImageProcessor, AutoModel
    except ImportError as e:  # pragma: no cover - depends on the environment
        raise SystemExit("dinov2 needs the deep extra: uv sync --extra deep") from e
    device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
    processor = AutoImageProcessor.from_pretrained(name)
    model = AutoModel.from_pretrained(name).to(device).eval()
    return processor, model, device


def _dinov2_clip(clip: Clip, fps: float, batch_size: int = 16) -> tuple[np.ndarray, np.ndarray]:
    import torch

    processor, model, device = _load_dinov2(DINOV2_MODEL)
    ts, rows, batch = [], [], []

    def flush():
        inputs = processor(images=batch, return_tensors="pt").to(device)
        with torch.no_grad():
            out = model(**inputs)
        rows.append(out.pooler_output.float().cpu().numpy())
        batch.clear()

    for t, rgb in sample_frames(clip, fps):
        ts.append(t)
        batch.append(rgb)
        if len(batch) == batch_size:
            flush()
    if batch:
        flush()
    return np.array(ts), np.concatenate(rows)


def cache_path(cache_dir: Path, backend: str, clip: Clip, fps: float) -> Path:
    # The ROI and event time change which pixels and frames are read, so they are part of the key.
    key = hashlib.sha1(repr((str(clip.path), clip.roi, clip.event_s, fps)).encode()).hexdigest()[:8]
    return cache_dir / "features" / backend / f"{clip.clip_id}-{key}.npz"


def clip_features(clip: Clip, backend: str, fps: float, cache_dir: Path) -> tuple[np.ndarray, np.ndarray]:
    """Return ``(t, X)`` for one clip, computing and caching on first use."""
    path = cache_path(cache_dir, backend, clip, fps)
    if path.exists():
        z = np.load(path)
        return z["t"], z["X"]
    if backend == "color":
        t, X = _color_clip(clip, fps)
    elif backend == "dinov2":
        t, X = _dinov2_clip(clip, fps)
    else:
        raise ValueError(f"unknown backend {backend!r}; choose from {BACKENDS}")
    if len(t) == 0:
        raise ValueError(f"{clip.clip_id}: no frames read from {clip.path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, t=t, X=X)
    return t, X
