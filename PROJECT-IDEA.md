# Project Idea: Self-Bootstrapping Real-Time Cooking Coach

**Status: Exploring (Research Program)**
**Timeline: 3 days to presentable demo**

---

## One-Liner

A real-time cooking coach where the AI doesn't just analyze video — it builds its own perception pipeline: generating state machines, deciding when to pay attention, and grading its own output.

## Thesis

Current real-time video AI treats every frame equally and requires hand-built domain knowledge. The missing layer is a system that teaches itself what to watch, when to watch, and what matters — using LLMs to bootstrap the entire perception pipeline instead of just sitting at the end of it.

## Pitch

"We don't use AI to analyze cooking. We use AI to build the AI that analyzes cooking — it generates its own state machine, decides when to pay attention, and grades its own output. The model isn't the product. The model that builds the model is."

---

## What It Actually Does

You start a cook. You tell the system what you're making ("chicken stir fry"). The system:

### 1. Generates Its Own State Machine

An LLM takes the recipe and produces a structured graph of every cooking state and transition: `oil cold -> oil hot -> oil smoking`, `chicken raw -> chicken searing -> chicken cooked through`, `vegetables crisp -> vegetables tender`. This graph is not hand-coded. It's generated fresh for every recipe.

### 2. Watches the Video Stream Locally at 30fps

A lightweight, cheap change detector runs on every frame. It doesn't understand cooking. It understands pixels. It detects when something visually meaningful changed: color shift in the pan, smoke appearing, new ingredient entering the frame.

### 3. Decides When to Think

When the change detector fires, a sampling policy decides whether this change is worth sending to an expensive multimodal LLM. It uses the current state to inform this decision. If the system knows you're in the "oil heating" phase, it watches for shimmer and smoke. If you're in the "dough resting" phase, it ignores almost everything for 20 minutes. The system doesn't call the API on a timer. It calls the API when something matters.

### 4. Maintains a Persistent World Model

Every LLM call doesn't start from zero. The system keeps a running state: what's on the stove, how long it's been there, what state each ingredient is in, what the next expected transition is. Each new LLM observation gets merged into this state incrementally. Frame 847 knows everything that happened in frames 1-846 without re-processing them.

Example state representation:

```json
{
  "active_processes": [
    {"item": "onions", "state": "browning", "started": 240, "expected_next": "caramelized", "eta_seconds": 180},
    {"item": "oil", "state": "hot", "risk": "smoking_soon"}
  ],
  "completed": ["garlic_minced", "onions_diced"],
  "next_step": "add garlic when onions are translucent"
}
```

### 5. Alerts Proactively, Before the Mistake

Because the system knows the state graph and the current state, it can predict what's about to go wrong. "Onions have been on high heat for 5 minutes and are approaching brown — reduce heat or they'll burn in 60 seconds." The alert comes before the failure, not after.

### 6. Grades Its Own Output

A secondary model evaluates whether the primary model's calls were accurate. Did the system say "onions are translucent" and then 2 minutes later they were already burnt? That's a timing error. This self-eval loop produces a quality score without any human labeling, creating a feedback signal for improving the system over time.

---

## Why This Is Different From "Send Frames to GPT-4V"

Anyone can call a multimodal API every 5 seconds and ask "what's happening." That's a weekend project. It's also:

- **Expensive** — 720 API calls per hour of cooking
- **Dumb** — samples uniformly whether or not anything changed
- **Stateless** — each call forgets everything before it
- **Reactive** — can only describe what it sees, not predict what's coming
- **Unvalidated** — no way to know if it's hallucinating

This system is the opposite on every axis. It generates its own domain knowledge, decides when to pay attention, remembers everything, predicts forward, and checks its own work.

---

## The Research Angle

### The Academic Gap

Temporal reasoning in video streams is an active research frontier (not unsolved, but not shipped):

- **TEMPURA** (2025) — temporal event masked prediction with causal reasoning
- **GraphThinker** (2026) — event graph-based temporal reasoning for video
- **Cooking state detection** (Sept 2026) — temporal visual features achieved 95.7% accuracy on 3-level cooking states, but didn't run on-device or in real-time
- **WeaveTime** (CVPR 2026) — streaming earlier frames into emergent memory in VideoLLMs
- **ViCoStream** (2026) — 134 FPS video throughput, <50ms latency on A100
- **CodecSight** (2026) — 87% GPU compute reduction via video codec signal reuse

The research exists in papers. Nobody has shipped it as a real-time product. The opportunity is being the bridge between academic temporal video understanding and a usable, deployed system.

### Novel Contributions

1. **LLM-as-test-oracle for streaming systems** — a second model grades the first model's real-time outputs without ground truth labels
2. **Model-generated state machines** — LLMs bootstrap the domain model (state graphs) instead of humans hand-coding them
3. **Synthetic training data from video models** — generate training examples for the change detector instead of filming them
4. **LLM-driven frame sampling policy** — the system learns when the expensive model would have said something useful and only calls it then

---

## Hardware vs Software Constraint

This is primarily a **software/architecture problem**, not hardware:

| Layer | Constraint | Details |
|-------|-----------|---------|
| Edge/on-device | Hardware | Can't run full VideoLLMs on consumer devices |
| Cloud inference | Memory bandwidth | GPU compute is underutilized — HBM bandwidth is the wall |
| Streaming pipeline | Software | Encode-decode-preprocess-inference-postprocess has ~5-8ms budget at 60fps |
| Frame selection | Software (mostly solved) | Smart sampling works in papers, not in products |
| Temporal state | Software (active frontier) | KV cache grows unboundedly over long streams |

The hardware to run this exists today (a single A100 does 134 FPS video understanding). The bottleneck is architectural — nobody has stitched smart frame sampling + temporal state tracking + multimodal LLM into a single real-time pipeline that works end-to-end.

---

## Tech Stack

| Layer | Tool | Why |
|-------|------|-----|
| Video capture | Laptop webcam via OpenCV | Simple, reliable, 30fps |
| Local change detector | Lightweight CNN or CLIP-based diff (Python) | Runs every frame, cheap. Detects meaningful visual change |
| Smart sampler | Custom Python service | Decides when to escalate a frame to the expensive model |
| State store | In-memory Python dict or Redis | Running world model: what's happening, how long, what's next |
| Reasoning model | Claude or GPT-4V via API | Only called when sampler triggers. Receives frame + full state context |
| State machine generator | Claude (one-shot, pre-runtime) | Recipe in -> state graph JSON out |
| Self-eval / oracle | Second LLM call (cheaper model) | Grades primary model's accuracy after the fact |
| UI | React + Tailwind via v0 | Live video feed, state timeline, alert cards, agent status |
| Backend glue | FastAPI + WebSocket | Streams frames, state updates, and alerts between backend and frontend |

---

## Hard Design Problems

### 1. Defining "Meaningful Change"

The local change detector must distinguish "person shifted slightly" (ignore) from "oil started shimmering" (escalate). Options:
- Frame-to-frame CLIP embedding distance (cosine similarity threshold)
- Pixel-diff in specific ROIs (region of interest around the pan)
- Small fine-tuned classifier on synthetic data

The threshold is context-dependent. "Nothing changed" when searing is different from "nothing changed" when dough is rising. The sampler needs to know the current state to know what change to look for.

### 2. Incremental State Updates

The world model must be updated incrementally from sparse LLM calls, not rebuilt from scratch. One LLM call says "onions look translucent now." The system must update state, advance the timeline, and change what the sampler watches for — all atomically.

### 3. State Machine Validation

When the LLM generates a state graph for a recipe:
- How do you validate correctness?
- How do you handle unpredicted states? (egg dropped on floor)
- One graph per recipe, or one universal cooking graph?

Best approach: one graph per recipe generated at cook start. Novel states get flagged and added at runtime.

### 4. Latency Budget

```
Frame captured             ->  0ms
Change detector runs       ->  ~10ms  (must be this fast)
Decision to escalate       ->  ~1ms
Frame + state sent to LLM  ->  ~1500ms round trip
State updated              ->  ~5ms
Alert rendered in UI       ->  ~50ms
                              --------
Total (when triggered):       ~1.6 seconds
```

1.6 seconds is fine for slow processes (burning, reducing, rising). Not fine for fast events (spills, cuts). Must be honest about scope.

### 5. The Eval Loop

The oracle sees: "at t=240s, system said 'onions are translucent.' At t=300s, frame shows onions are brown." Grading rubric: `{timing: early/correct/late, accuracy: correct/wrong/hallucinated}`.

---

## Demo

You cook an omelette live. The system generates the state machine on screen ("eggs cracked -> eggs whisked -> butter melting -> eggs poured -> eggs setting -> fold -> plate"). The audience watches the state timeline advance in real-time. The system stays silent when nothing is happening. The moment the butter starts browning too fast, it speaks: "Butter is browning — pour your eggs now or reduce heat." No one prompted it. No one asked. It knew because it built its own understanding of what matters.

---

## 3-Day Build Plan

| Day | Deliverable |
|-----|------------|
| Day 1 | Webcam -> OpenCV -> frame diff change detector -> Claude API call on trigger -> print output to terminal. Ugly but working. |
| Day 2 | State store + incremental updates. State machine generation from recipe input. React UI with live feed + state timeline + alerts. |
| Day 3 | Self-eval loop. Tune the sampler. Polish UI. Rehearse demo. |

The MVP that proves the thesis is just Day 1: a system that doesn't call the API every frame but still catches the important moments.

---

## Competitive Landscape (Past Hackathon Winners)

| Project | What It Did | How We're Different |
|---------|------------|-------------------|
| Cosmo Cook (Google x MHacks 2024, 1st) | AI cooking assistant using Gemini | Reactive Q&A, not proactive vision-based coaching |
| Hardware Context Protocol (Cal Hacks 12) | Voice-activated autonomous chef robot | Robot does the cooking. We coach the human. |
| plaite (MHacks 2024) | Food recognition + nutritional info via CV | Single-frame classification, no temporal reasoning |
| Fight and Furious (HackGT 11) | Krav Maga coaching via CV | Same archetype (real-time coaching via vision) but no self-bootstrapping pipeline |
| Conversenses (MHacks 2025) | Real-time public speaking coaching via AR | Same archetype, different domain |

No winner has built a system where the LLM generates its own perception pipeline. The self-bootstrapping angle is genuinely novel.

---

## Sources

- [Temporal visual feature-guided cooking state detection (Sept 2026)](https://link.springer.com/article/10.1007/s11694-026-04917-3)
- [ViCoStream: Streaming VideoLLMs beyond 100 FPS](https://arxiv.org/html/2606.19849v1)
- [CodecSight: Leveraging Video Codec Signals for VLM Inference](https://arxiv.org/html/2604.06036v3)
- [WeaveTime: Streaming into Emergent Memory (CVPR 2026)](https://openaccess.thecvf.com/content/CVPR2026/papers/Zhang_WeaveTime_Streaming_from_Earlier_Frames_into_Emergent_Memory_in_VideoLLMs_CVPR_2026_paper.pdf)
- [TEMPURA: Temporal Event Masked Prediction](https://arxiv.org/pdf/2505.01583)
- [GraphThinker: Event Graph Thinking for Video Reasoning](https://arxiv.org/pdf/2602.17555)
- [OSCAR: Object Status and Contextual Awareness for Recipes](https://arxiv.org/pdf/2503.05962)
- [Wearable Multi-Modal Edge System for Kitchen Activity Recognition](https://arxiv.org/pdf/2409.06341)
