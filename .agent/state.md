# Working State

## Current objective

Vision-only time-to-finish prediction vs a clock baseline (see `task.md`).

## Status

- Phase: verification (synthetic); waiting on real clips

## Completed

- `foresight` package: synth, features (color, dinov2), clock + ridge models, leave-one-clip-out evaluate, figure, demo video.
- Synthetic run (8 clips, seed 0, 2 fps): clock MAE 32.6 s, color 21.1 s, color beats clock on 7/8 clips.

- DINOv2 path smoke-tested offline with random weights under transformers 5.19: 384-d features, about 7 frames/s on 4 CPU cores.
- Vision predictions are capped at 1.5x the longest training wait (log-space ridge blew up on a 1-clip training set).

## Active assumptions

- [ASSUMPTION] Ridge on causal features is enough for a first result; a GRU head is a possible next step.

## Verified facts

- [FACT] huggingface.co and download.pytorch.org are blocked by the cloud container's network policy, so DINOv2 weights cannot be downloaded there. They download normally on a laptop.

## Next concrete action

Film 4–5 clips per process (see README filming checklist), write `data/clips/labels.csv`, run `foresight evaluate --backends color,dinov2`.
