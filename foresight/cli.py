"""Command line: ``python -m foresight <command>`` (or ``uv run foresight <command>``)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from . import demo, evaluate, plots, synth
from .data import load_labels
from .features import BACKENDS


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(prog="foresight", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("synth", help="generate synthetic browning clips to test the pipeline")
    s.add_argument("--out", type=Path, default=Path("data/synth"))
    s.add_argument("--n", type=int, default=8)
    s.add_argument("--seed", type=int, default=0)

    def common(q):
        q.add_argument("--labels", type=Path, required=True, help="CSV of clips (see foresight/data.py)")
        q.add_argument("--results", type=Path, default=Path("results"))

    e = sub.add_parser("evaluate", help="extract features, train leave-one-clip-out, score, plot")
    common(e)
    e.add_argument("--backends", default="color", help=f"comma list from {','.join(BACKENDS)}")
    e.add_argument("--fps", type=float, default=2.0, help="frames sampled per second")
    e.add_argument("--cache", type=Path, default=Path("cache"))
    e.add_argument("--pool", action="store_true", help="train on all other clips, not just the same process")
    e.add_argument("--tol", type=float, default=evaluate.LOCK_TOL_S, help="lock-on tolerance in seconds")

    d = sub.add_parser("demo", help="render the countdown video for one held-out clip")
    common(d)
    d.add_argument("--clip", required=True)
    d.add_argument("--model", default="color")

    args = p.parse_args(argv)
    if args.cmd == "synth":
        labels = synth.generate(args.out, n=args.n, seed=args.seed)
        print(f"wrote {args.n} clips; labels at {labels}")
    elif args.cmd == "evaluate":
        backends = [b.strip() for b in args.backends.split(",") if b.strip()]
        clips = load_labels(args.labels)
        _, predictions = evaluate.run(clips, backends, args.fps, args.cache, args.results, args.pool, args.tol)
        fig = plots.countdown_panels(predictions, args.results / "countdowns.png")
        print((args.results / "summary.md").read_text())
        print(f"per-clip metrics: {args.results / 'metrics_per_clip.csv'}\nfigure: {fig}")
    elif args.cmd == "demo":
        clips = {c.clip_id: c for c in load_labels(args.labels)}
        if args.clip not in clips:
            raise SystemExit(f"unknown clip {args.clip!r}; have {', '.join(clips)}")
        predictions = pd.read_csv(args.results / "predictions.csv")
        out = demo.render(clips[args.clip], predictions, args.model, args.results / f"demo_{args.clip}_{args.model}.mp4")
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
