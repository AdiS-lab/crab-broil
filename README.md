# Foresight: can a camera see when dinner will be done?

Point a camera at a pan. With no recipe, no language model and no timer, show a
live countdown: **"BROWNING IN 0:47 … 0:46 …"**, and have it hit zero when the
butter actually browns.

The research question is whether the model is **seeing the future or just
counting**. Activity-progress models have been caught doing the second:
[de Boer et al. (ICCVW 2023)](https://arxiv.org/abs/2308.05533) found they did
not beat a frame-counting baseline on real datasets, and only used visual cues
when those cues were actually tied to progress (on synthetic data). Cooking is a
natural real-world test, because browning, boiling and melting are progress you
can physically see. Every model here is scored against that frame-counting
"clock". Pixels have to beat it.

Labels are nearly free, as in [RSDNet (Twinanda et al.)](https://arxiv.org/abs/1802.03243):
you mark the one moment each clip finishes, and every earlier frame's target is
"seconds left until then".

## Pipeline

```
video ─► sample frames (2 fps) ─► frozen features ─► causal design ─► ridge regression ─► countdown
           crop to the pan          color stats         look now          log(seconds left)    causal median
                                    or DINOv2 CLS       change since start                     on the finish time
                                                        change in last 10 s
```

Models compared, all evaluated leave-one-clip-out:

| model | sees | question it answers |
|---|---|---|
| `clock` | elapsed time only | the bar to beat: average time left at this moment in the training clips |
| `color` | hand-crafted color, texture and motion statistics | do simple pixels beat the clock? |
| `dinov2` | frozen pretrained DINOv2-small embedding | do learned visual features beat simple pixels? |
| `*+clock` | the same plus elapsed time | does vision add anything on top of the clock? |

Metrics per held-out clip, before the event:

- **error, all frames**: mean |predicted − true| seconds left
- **error, last 60 s**: the same, only where it matters for an alert
- **lock**: for how many seconds before the event the countdown stays within ±10 s
- **clips beating clock**: on how many clips the model's error is lower than the clock's

## Setup

```bash
uv sync                  # color backend only
uv sync --extra deep     # adds torch + transformers for DINOv2 (weights download from huggingface.co once)
```

## Test it on synthetic clips first

```bash
uv run foresight synth                                       # 8 clips in data/synth/, each browning at its own speed
uv run foresight evaluate --labels data/synth/labels.csv     # prints the results table, writes results/
uv run foresight demo --labels data/synth/labels.csv --clip synth_00 --model color
```

Synthetic results only prove the code works and that vision *can* beat the clock
when the cue is real. They say nothing about real cooking.

## Your real clips

1. Put videos in `data/clips/` and write `data/clips/labels.csv`:

   ```csv
   clip_id,file,process,event_s,roi
   butter_01,butter_01.mp4,browning,142.5,410,260,500,380
   butter_02,butter_02.mp4,browning,97.0,400,250,520,390
   ```

   `event_s` is the second the process finishes, read off the video player.
   `roi` is `x,y,w,h` in video pixels around the pan; leave it empty for the full frame.

2. Run:

   ```bash
   uv run foresight evaluate --labels data/clips/labels.csv --backends color,dinov2
   uv run foresight demo --labels data/clips/labels.csv --clip butter_01 --model dinov2
   ```

Outputs land in `results/`: `summary.md` (the table for the write-up),
`metrics_per_clip.csv`, `predictions.csv`, `countdowns.png` and the demo mp4.

## Filming checklist

The experiment is only as good as the clips. The point is to make the clock fail.

- **Pick 1–2 processes and film 4–5 clips of each**, not one clip each of many.
  Leave-one-out needs other clips of the same process to learn from.
  Good choices: butter browning, water coming to a boil, toast in a dry pan, onions softening.
- **Vary how long each clip takes.** Change the heat, the amount, the pan. If every
  clip finishes at 2:00, the clock wins by definition and the experiment shows nothing.
- **Start recording the moment the heat goes on** (or the food goes in), so time 0 means the same thing in every clip.
- **Fix the camera.** Tripod or phone propped up, same angle each time, pan filling a good part of the frame.
- **Keep the lighting steady.** Kitchen lights on, avoid a window with changing daylight, lock exposure if the phone allows (tap and hold on iPhone).
- **Keep hands out of the shot** as much as possible. Brief stirs are fine.
- **Keep recording ~15 s past the moment it's done**, then write down that moment.
- 2–5 minutes per clip is plenty. Landscape, 1080p or 720p.

## Layout

```
foresight/
  data.py       labels CSV, frame sampling, ROI crop
  features.py   color and DINOv2 features, cached in cache/
  models.py     clock baseline, vision ridge regressor, causal smoothing
  evaluate.py   leave-one-clip-out training, metrics, results table
  plots.py      predicted-vs-true countdown figure
  demo.py       countdown overlay video
  synth.py      synthetic browning clips
  cli.py        foresight synth | evaluate | demo
```
