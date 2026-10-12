# Active Task

## Objective

Scaffold and verify a pipeline that trains and evaluates vision-only time-to-finish predictors against a clock baseline, ready to run on clips filmed tonight.

## Why

The research deliverable is due tonight. The thesis: a model can see when a cooking process will finish, not just count time.

## Current state

Pipeline exists and runs end to end on synthetic clips. No real clips yet.

## Required behavior

1. `foresight synth` produces labelled synthetic clips with varied finish times.
2. `foresight evaluate` extracts features, trains leave-one-clip-out, and writes a results table, per-clip metrics, predictions and a figure.
3. `foresight demo` renders a countdown overlay video for a held-out clip.

## Acceptance criteria

- [x] Full synthetic run completes and the color model beats the clock on synthetic data
- [x] Demo video renders
- [x] DINOv2 code path runs end to end (checked with randomly initialised DINOv2-small weights, 384-d output)
- [ ] DINOv2 backend runs with real pretrained weights (needs huggingface.co access; blocked in the cloud container)
- [ ] Real clips filmed, labelled and evaluated

## Verification

`uv run foresight synth && uv run foresight evaluate --labels data/synth/labels.csv`, then inspect `results/summary.md` and `results/countdowns.png`.

## Known unknowns

- Whether real clips vary enough in duration for the clock to fail
- Whether 4–5 clips per process is enough for DINOv2 + ridge without overfitting
