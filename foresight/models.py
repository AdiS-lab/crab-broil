"""Predictors of time-to-event (seconds until the process finishes).

- ``ClockBaseline`` sees no pixels. It is the frame-counting baseline from
  de Boer et al. (ICCVW 2023): at elapsed time t it predicts the average time
  left at t over the training clips that had not finished yet. If a vision model
  cannot beat this, it is counting, not seeing.
- ``VisionRegressor`` sees only pixels: a ridge regression on the frozen features
  of the recent frames. With ``use_clock=True`` it also gets elapsed time, to
  measure whether vision adds anything on top of the clock.
"""

from __future__ import annotations

import numpy as np
from sklearn.linear_model import RidgeCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

SMOOTH_S = 3.0  # average features over this many seconds to cut per-frame noise
BASELINE_S = 5.0  # "what it looked like at the start" for change-since-start
LAG_S = 10.0  # "how fast it is changing": now vs this many seconds ago
OUTPUT_SMOOTH_S = 5.0  # causal median on the predicted finish time


def _step(t: np.ndarray) -> float:
    return float(np.median(np.diff(t))) if len(t) > 1 else 1.0


def design(t: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Causal per-frame inputs: smoothed look now, change since start, recent change.

    Every row uses only frames at or before its own time, so predictions could run live.
    """
    step = _step(t)
    w = max(1, round(SMOOTH_S / step))
    n0 = max(1, round(BASELINE_S / step))
    lag = max(1, round(LAG_S / step))

    csum = np.cumsum(np.vstack([np.zeros((1, X.shape[1]), X.dtype), X]), axis=0)
    idx = np.arange(len(X))
    lo = np.maximum(0, idx - w + 1)
    cur = (csum[idx + 1] - csum[lo]) / (idx + 1 - lo)[:, None]
    nb = np.minimum(idx + 1, n0)
    base = csum[nb] / nb[:, None]
    vel = cur - cur[np.maximum(0, idx - lag)]
    return np.hstack([cur, cur - base, vel])


def time_to_event(t: np.ndarray, event_s: float) -> np.ndarray:
    return np.maximum(event_s - t, 0.0)


class ClockBaseline:
    name = "clock"

    def fit(self, event_times: list[float]) -> "ClockBaseline":
        self.event_times = np.asarray(event_times, dtype=float)
        return self

    def predict(self, t: np.ndarray) -> np.ndarray:
        left = self.event_times[None, :] - t[:, None]
        alive = left >= 0
        n = alive.sum(1)
        return np.where(n > 0, np.where(alive, left, 0).sum(1) / np.maximum(n, 1), 0.0)


class VisionRegressor:
    def __init__(self, backend: str, use_clock: bool = False):
        self.backend = backend
        self.use_clock = use_clock
        self.name = backend + ("+clock" if use_clock else "")

    def _inputs(self, t: np.ndarray, X: np.ndarray) -> np.ndarray:
        D = design(t, X)
        return np.hstack([D, t[:, None]]) if self.use_clock else D

    def fit(self, clips: list[tuple[np.ndarray, np.ndarray, float]]) -> "VisionRegressor":
        """``clips`` is a list of ``(t, X, event_s)``."""
        D = np.vstack([self._inputs(t, X) for t, X, _ in clips])
        # Log target: being 10 s off matters near the event, much less 5 minutes out.
        y = np.concatenate([np.log1p(time_to_event(t, e)) for t, _, e in clips])
        self.model = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 5, 15)))
        self.model.fit(D, y)
        return self

    def predict(self, t: np.ndarray, X: np.ndarray) -> np.ndarray:
        return np.maximum(np.expm1(self.model.predict(self._inputs(t, X))), 0.0)


def smooth_countdown(t: np.ndarray, tte: np.ndarray) -> np.ndarray:
    """Causal median of the predicted finish time (t + tte), turned back into a countdown.

    Smoothing the finish time rather than the countdown keeps a correct prediction
    steady while the countdown itself ticks down.
    """
    k = max(1, round(OUTPUT_SMOOTH_S / _step(t)))
    finish = t + tte
    smoothed = np.array([np.median(finish[max(0, i - k + 1) : i + 1]) for i in range(len(t))])
    return np.maximum(smoothed - t, 0.0)
