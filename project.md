# Project Context

## Name

Foresight (repo: crab-broil)

## One-line purpose

Predict how many seconds until a cooking process finishes (browning, boiling) from video pixels alone, and test whether that beats simply counting elapsed time.

## Current stage

Research prototype for a project due the same day. `PROJECT-IDEA.md` is the original, broader pitch (LLM-built state machines, sampling policy, self-grading); this narrower vision-only thesis replaced it.

## Stack

- Runtime: Python 3.11+, managed with `uv`
- Video: OpenCV
- Features: hand-crafted color/texture/motion stats; frozen DINOv2-small via `transformers` + `torch` (optional `deep` extra)
- Learning: scikit-learn ridge regression
- Analysis: pandas, matplotlib
- Backend / data / deployment: none. Local files only.

## Architecture

1. `data.py` reads a labels CSV (one hand label per clip: the second it finishes) and samples frames at 2 fps, cropped to the pan.
2. `features.py` turns each frame into a feature vector (never the timestamp) and caches it under `cache/`.
3. `models.py` builds causal inputs (now, change since start, change over the last 10 s) and fits ridge regression on log(seconds left). `ClockBaseline` is the frame-counting baseline from de Boer et al. (ICCVW 2023).
4. `evaluate.py` runs leave-one-clip-out, scores error, last-60 s error and lock-on time, and writes `results/`.
5. `demo.py` overlays the held-out countdown on the video.

## Important directories

| Path | Purpose |
|---|---|
| `foresight/` | the pipeline package |
| `data/clips/` | real videos + `labels.csv` (gitignored) |
| `data/synth/` | generated synthetic clips (gitignored) |
| `cache/`, `results/` | cached features and outputs (gitignored) |
| `docs/other-projects/` | research for an unrelated project, kept for reference |

## Important commands

```text
Install: uv sync [--extra deep]
Synthetic test: uv run foresight synth && uv run foresight evaluate --labels data/synth/labels.csv
Real data: uv run foresight evaluate --labels data/clips/labels.csv --backends color,dinov2
Demo: uv run foresight demo --labels <csv> --clip <id> --model <name>
Test / lint / typecheck: none set up
```

## Environment

No API keys. The `dinov2` backend downloads `facebook/dinov2-small` from huggingface.co on first use.

## Stable constraints

- Vision only at prediction time: no recipe text, no language model, no timer input (except the explicit `clock` baseline and `+clock` variants).
- Every reported result is leave-one-clip-out and compared against the clock baseline.
- Predictions are causal: each uses only frames at or before its own time.

## Explicit non-goals

- Live webcam app, server or UI
- LLM-generated recipe state machines, sampling policies, self-grading (from `PROJECT-IDEA.md`)
- Fine-tuning the vision encoder
