"""Synthetic "butter browning in a pan" clips for testing the pipeline end to end.

Each clip browns at its own random speed, so elapsed time alone cannot tell when
it will finish but the pixels can. This mirrors the controlled synthetic setting
in de Boer et al. (ICCVW 2023). It checks the code and the claim that vision can
beat the clock when the visual cue is real. It is NOT evidence about real cooking.
"""

from __future__ import annotations

import csv
from pathlib import Path

import cv2
import numpy as np

W, H, FPS = 320, 240, 10
ROI = (70, 30, 180, 180)
PALE, GOLDEN, BROWN, BURNT = (np.array(c, float) for c in [(240, 222, 150), (214, 160, 70), (120, 66, 24), (45, 28, 15)])


def food_color(p: float) -> np.ndarray:
    """Pale at p=0, golden at 0.5, brown at 1 (the event), burnt by 1.5."""
    stops = [(0.0, PALE), (0.5, GOLDEN), (1.0, BROWN), (1.5, BURNT)]
    p = float(np.clip(p, 0, 1.5))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
        if p <= p1:
            return c0 + (c1 - c0) * (p - p0) / (p1 - p0)
    return BURNT


def render_clip(path: Path, event_s: float, rng: np.random.Generator, post_s: float = 10.0) -> None:
    gain = rng.uniform(0.8, 1.2)  # lighting differs between clips
    gamma = rng.uniform(0.8, 1.4)  # browning speeds up or slows down
    p0 = rng.uniform(0.0, 0.1)
    spatula_at = rng.uniform(5, event_s) if rng.random() < 0.6 else None

    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"mp4v"), FPS, (W, H))
    for i in range(int((event_s + post_s) * FPS)):
        t = i / FPS
        p = p0 + (1 - p0) * (t / event_s) ** gamma
        light = gain * (1 + 0.03 * np.sin(t / 7))
        img = np.full((H, W, 3), 150.0)
        cv2.circle(img, (160, 120), 88, (45, 45, 48), -1)
        cv2.ellipse(img, (160, 120), (60, 46), 0, 0, 360, food_color(p)[::-1].tolist(), -1)
        for _ in range(int(4 + 30 * min(p, 1.2))):  # sizzle: more bubbles as it heats
            cx, cy = rng.normal(160, 25), rng.normal(120, 18)
            cv2.circle(img, (int(cx), int(cy)), 1, (235, 240, 245), -1)
        if spatula_at is not None and spatula_at <= t < spatula_at + 2:
            x = int(40 + 240 * (t - spatula_at) / 2)
            cv2.rectangle(img, (x, 60), (x + 25, 230), (90, 90, 90), -1)
        img = img * light + rng.normal(0, 6, img.shape)
        dx, dy = rng.integers(-2, 3, size=2)
        img = np.roll(img, (dy, dx), axis=(0, 1))
        writer.write(np.clip(img, 0, 255).astype(np.uint8))
    writer.release()


def generate(out_dir: Path, n: int = 8, seed: int = 0, min_s: float = 60, max_s: float = 200) -> Path:
    rng = np.random.default_rng(seed)
    clips_dir = out_dir / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    labels = out_dir / "labels.csv"
    with labels.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["clip_id", "file", "process", "event_s", "roi"])
        for k in range(n):
            clip_id = f"synth_{k:02d}"
            event_s = round(float(rng.uniform(min_s, max_s)), 1)
            render_clip(clips_dir / f"{clip_id}.mp4", event_s, rng)
            w.writerow([clip_id, f"clips/{clip_id}.mp4", "browning", event_s, ",".join(map(str, ROI))])
    return labels
