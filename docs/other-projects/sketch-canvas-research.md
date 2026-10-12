# Research: Sketch-and-Reference Canvas for Atomic Assets

> Research into the I2P application's idea: a canvas where you sketch and drop references in place of prompts, and a model works in a loop until it produces one usable asset (SVG, shader, video effect, component).
> Researched 2026-09-30. Figures are from the sources linked below. Where something is an estimate or an assumption, it is labelled.

## 1. Summary

- **The core technical bet has independent support.** Research published in 2026 finds that letting a model *see its own rendered output* improves SVG quality more than training on more data (see §3). This is the strongest evidence for the "render → compare → revise" loop.
- **The market is more crowded than the application says.** Figma, tldraw, Kling, Flora, Krea and Recraft all ship canvas or loop-style AI tools. Recraft already sells native SVG generation for $0.08 per image. What sets this project apart has to be **atomic, exportable, editable assets + cheap iteration + human steering**, not "a canvas."
- **Three statistics in the draft need fixing** before submission (§6): Shutterstock's growth rate, the "~$2B for reusable assets" framing, and the merger context.
- **The $0.50 / 15–20 iteration budget looks feasible for SVG, but only under specific design choices**: a cheap vision model, small render sizes, prompt caching, and edits instead of full rewrites. Calling an image-generation model on every iteration would blow the budget (§4).
- **Loops left to run on their own drift toward generic output** (§3.3). This directly supports the "human stays in the loop" design and the anti-sameness argument. It also means the loop must stay anchored to the user's references.

## 2. Competitive landscape

| Product | What it does | Overlap with this idea | Gap this project could fill |
|---|---|---|---|
| **tldraw Make Real / canvas agents** | Turns sketches and annotations into working HTML/CSS/JS. In 2026 it shows multiple agents working on a shared canvas. | Very high: this is sketch → code on a canvas | Output is whole UIs, not reusable assets. No loop that scores results against a reference. |
| **Figma Make + "canvas open to agents" (Mar 24, 2026)** | Prompt → prototype/app. The `use_figma` MCP tool gives coding agents write access to Figma files. A Skills framework was added. | High, for UI components | Tied to Figma's ecosystem and design system. Not aimed at shaders, effects or standalone SVG. |
| **Figma Weave (formerly Weavy, acquired for >$200M)** | Node canvas that chains image, video, audio and 3D models | Medium: a canvas plus iteration | Pixel and video output, and expensive per generation |
| **Kling canvas / Kling 3 Omni (Aug 2026)** | Video-first node canvas with "Continue in Canvas" | Low to medium | Video generation. This is the slow, expensive path the application argues against. |
| **Flora ($42M Series A, Jan 2026)** | Node-based design tool for image, text and video assets | Medium | Raster and video media, not code assets |
| **Krea** | Node editor plus real-time generation | Medium | Raster |
| **Recraft V4 / V4.1 (Feb and May 2026)** | Text → native SVG with editable paths. V3 Vector API costs $0.08 per image. | **Direct competitor for the SVG MVP** | One-shot from a prompt. No sketch input, no loop that compares results to a reference, no path to shaders or components. |
| **Adobe Firefly Text to Vector** | Text → editable SVG inside Illustrator | High, for SVG | Prompt-only, inside Adobe's suite |
| **Poppy AI** | Multiplayer canvas for marketing content | Low | Aimed at text and marketing content |
| **21st.dev / shadcn registries** | Community marketplace and registry for components. Any GitHub repo with a `registry.json` becomes installable. It already has an MCP for agents. | **Distribution and marketplace layer** | No generation from sketches. This is a possible export target, not a rival. |
| **AI Co-Artist (research)** | GPT-4 evolves GLSL shaders while the user picks the versions they like | High, for the shader asset class | Research prototype. Selection only, with no reference image to match. |

**What this means:** The claim that incumbents are "not incentivized" to build this is weak. Figma is clearly building canvas + agents. A more defensible position:
1. **One asset, finished.** Competitors either produce whole apps (Make, Make Real) or raw media (Weave, Kling, Flora). Nobody is focused on a single editable asset that you can export as code.
2. **The loop is scored against the user's own references,** not just a prompt. Recraft and Firefly work one shot at a time.
3. **Cost.** A text-only format like SVG can go through many cheap rounds, where raster or video generation cannot.
4. **Export into places that already distribute components** (a shadcn-style registry, npm, Lottie) instead of building a marketplace from scratch.

## 3. Technical evidence for the loop

### 3.1 Seeing its own render helps more than more data
- *Render-in-the-Loop* (2026) turns SVG generation into a series of steps: the model sees the canvas rendered so far before adding each shape. A model trained on 0.85M samples **beat OmniSVG and InternSVG, which were trained on 16M**. The authors conclude visual feedback matters more than data scale. It also uses "Render-and-Verify" at inference time to filter out broken or duplicate shapes.
- *IntroSVG* (2026) pairs a generator with a critic that learns from rendered results and refines the SVG over several rounds.
- *Rendering-Aware RL for vector graphics* (NeurIPS 2025) uses rendered output as the training reward.

### 3.2 General LLMs are only moderately good at raw SVG
- **SVGenius** (22 models) found every model gets worse as SVG complexity rises, and style transfer is the hardest task. Proprietary models beat open-source ones, and reasoning-focused training helped more than size.
- **VGBench** found LLMs do much better with higher-level formats (TikZ, Graphviz) than with low-level SVG paths.
- **Design implication:** Have the model work in a *higher-level intermediate form* (named shapes, groups, parameters) and compile that to SVG, rather than having it write path data directly. Keep assets small. This also makes changes between versions easier to read.

### 3.3 Autonomous loops drift toward generic output
- Hintze et al. (2025) ran text → image → text loops (SDXL + LLaVA) 700 times for 100 rounds each. **They all converged to about 12 generic "commercially safe" motifs**, which the authors call "visual elevator music." This held across model pairs, temperatures and longer prompts.
- **Design implication:** This is evidence *for* the pitch's anti-sameness argument, and a warning for the build. The loop must:
  - re-check against the user's original references every round, not only against the previous round;
  - stop and hand control back to the user after a few rounds;
  - never re-describe the image in words as the only signal passed to the next round.

### 3.4 Measuring "how close is it"
- Pixel metrics (SSIM, and LPIPS to a lesser extent) miss differences in layout, pose and meaning. **DreamSim** was trained on about 20k human judgments and matches human similarity ratings better than LPIPS, CLIP or DINO.
- A rough sketch is *not* a picture of the target, so no single pixel metric fits. Suggested scoring:
  1. **Structure against the sketch:** compare edges or silhouettes (e.g. IoU of rasterized masks).
  2. **Style against the references:** DreamSim or CLIP embeddings.
  3. **A VLM judge** that returns a structured list of differences ("stroke too thick in the top-left group"). That list becomes the next edit instruction.
- The harness decides when to stop. The human remains the final judge.

## 4. Cost model for the $0.50 / 15–20 iteration target

**Assumptions (estimates, not measured):**
- Each iteration sends the system prompt, the user's sketch, 1–2 references, the current render and the current SVG code, and gets back an edit.
- Images are downscaled to about 768×768.
- Per Anthropic's docs, an image costs about `width×height/750` tokens, so ~790 tokens each.
- SVG code is about 3k tokens.

| Configuration | Input tokens / iter | Output tokens / iter | ≈ Cost / iter | ≈ Cost / 20 iters |
|---|---|---|---|---|
| Claude Haiku 4.5 ($1 / $5 per M), full SVG rewrite | ~9k | ~3k | ~$0.024 | **~$0.48** |
| Claude Haiku 4.5, edits only + cached fixed context | ~9k (mostly cached) | ~0.6k | ~$0.006–0.01 | **~$0.12–0.20** |
| Claude Sonnet 4.5 ($3 / $15), full rewrite | ~9k | ~3k | ~$0.072 | ~$1.44 |
| Gemini 3.1 Flash-Lite ($0.25 / $1.50), full rewrite | ~9k | ~3k | ~$0.007 | ~$0.14 |
| + one image-generation call each iteration (Gemini Flash Image ≈ $0.04–0.045 per image) | — | — | +~$0.04 | **+~$0.80** |
| Recraft V3 Vector, one-shot, for comparison | — | — | $0.08 per SVG | $1.60 for 20 tries |

**What this suggests:**
- Asking for **edits instead of full rewrites** and **caching the fixed context** are the two biggest cost levers.
- **Tiered setup:** a cheap model makes the edits and a cheap VLM scores them. A stronger model is called only when progress stalls.
- **Generate a raster "target image" once or twice at most**, not every round.
- The first thing to validate in the semester is a simple experiment: run these configurations on 10–20 fixed sketch + reference tasks and log cost, number of iterations, and whether the result was kept.

## 5. MVP scope check (SVG)

Why SVG makes sense for the MVP:
- It's text, so it's cheap to generate and you can diff one version against another.
- It renders in a browser with no GPU.
- It's immediately useful in web, video and print work.
- A strong competitor (Recraft) sets a clear bar to beat.

**Scope boundaries to decide:**
- Input: freehand strokes + dropped images + optional short text
- Output: one SVG under N shapes, with named groups
- Loop: render → score → edit, capped at K rounds, then hand back to the user
- Export: an `.svg` file, a React component, and a shadcn-registry entry

**Risks:**
- Complex illustrations quickly exceed what LLM-written SVG can handle (§3.2). Start with icons, logos and simple spot illustrations.
- A sketch doesn't define the target clearly, so scoring against it is noisy.
- Recraft or Figma may add sketch input.
- Shaders and video effects need a very different renderer and scoring setup, so keep them out of MVP scope.

## 6. Fact-check of the draft application

| Claim in draft | Verified? | Correction / note |
|---|---|---|
| 56% trust national news, down 11 pts since Mar 2025 | ✅ Pew (Oct 2025) | Also down 20 pts since 2016 |
| 38% get news on Facebook, 35% YouTube, 20% Instagram, 20% TikTok | ✅ Pew (Aug 18–24, 2025 survey) | — |
| 43% of under-30s regularly get news on TikTok, up from 9% in 2020 | ✅ Pew (Sep 2025) | — |
| Young adults trust social media about as much as national news | ⚠️ Not confirmed in the sources I could reach | Cite the exact Pew page, or soften the wording |
| Shutterstock 2025 revenue $989.9M, **up 16%** | ❌ | Total revenue was up **6%**. The 16% was the Data, Distribution & Services segment only. Content revenue was $786.7M (+4%). |
| Getty 2025 revenue $981.3M; Creative $556.9M, +0.7% | ✅ | Total revenue +4.5% |
| "Roughly two billion dollars a year flows toward reusable visual assets" | ⚠️ | $989.9M + $981.3M ≈ $1.97B, but that includes editorial and data licensing. Creative/content alone is about $1.34B ($786.7M + $556.9M). Either say "the two largest stock companies together earn ~$2B" or use the content-only figure. |
| (context) | — | Getty abandoned its $3.7B merger with Shutterstock on Jul 1, 2026 after the UK CMA demanded a divestiture. That's worth a line: incumbents are consolidating, not innovating. |
| "Incumbents are unlikely to build this" | ⚠️ | Figma (Make, Weave, agents on canvas) and tldraw are actively building nearby products. Reframe as "incumbents build whole apps or raw media; nobody owns finished atomic assets." |
| "Models have only just become good enough to complete visual loops" | ✅ Supported by the 2026 render-in-the-loop work | Cite Render-in-the-Loop / IntroSVG |

## 7. Suggested semester metrics (fits the draft's goals)

- **Cost:** median $ per kept asset, iterations per kept asset, and wall-clock time per iteration, for each model configuration
- **Quality:** share of sessions that end in an export. Share of exports rated "would use as-is" vs. "needed manual edits." The DreamSim score against the references at export.
- **Retention (30 creators):** share returning for a second session within 14 days, and exported assets later found in shipped work (self-reported, with a link)
- **Interviews (12–14):** structure them around the moments where users gave up, re-sketched, or fell back to typing

## 8. Open questions

- What is the right *intermediate form* for SVG (raw SVG, a shape DSL, or parameterized primitives)? This affects cost, diff quality and success rate.
- Does a single VLM judge give scores that users agree with? This needs a small labelled set.
- Licensing and provenance of references users drop on the canvas. This matters if assets are sold in a marketplace.
- Is the second asset class shaders (the founders' origin story) or React components (closest to the shadcn distribution channel)?

## Sources

- Pew – trust in news orgs & social media (Oct 2025): https://www.pewresearch.org/short-reads/2025/10/29/how-americans-trust-in-information-from-news-organizations-and-social-media-sites-has-changed-over-time/
- Pew – Social media and news fact sheet (2025): https://www.pewresearch.org/journalism/fact-sheet/social-media-and-news-fact-sheet/
- Pew – 1 in 5 Americans regularly get news on TikTok (Sep 2025): https://www.pewresearch.org/short-reads/2025/09/25/1-in-5-americans-now-regularly-get-news-on-tiktok-up-sharply-from-2020/
- Shutterstock FY2025 results: https://shutterstock.gcs-web.com/node/14551 · https://finance.yahoo.com/news/shutterstock-sstk-reports-989-9m-114655765.html
- Getty Images FY2025 results: https://newsroom.gettyimages.com/en/getty-images/getty-images-reports-fourth-quarter-and-full-year-2025-results · https://www.sec.gov/Archives/edgar/data/1898496/000162828026018160/gety-20251231.htm
- Getty abandons Shutterstock merger: https://gdeltcloud.com/events/getty-images-abandons-37-billion-merger-with-shutterstock--cameoplus_4c1b6b6b · https://finance.yahoo.com/markets/stocks/articles/getty-images-gety-shutterstock-merger-105429531.html
- Render-in-the-Loop (2026): https://arxiv.org/abs/2604.20730
- IntroSVG (2026): https://arxiv.org/html/2603.09312
- Rendering-Aware RL for Vector Graphics (NeurIPS 2025): https://neurips.cc/virtual/2025/poster/120143
- SVGenius: https://arxiv.org/abs/2506.03139 · VGBench: https://arxiv.org/abs/2407.10972
- OmniSVG: https://arxiv.org/html/2504.06263v1 · StarVector: https://github.com/joanrod/star-vector
- Hintze et al., "Autonomous language-image generation loops converge to generic visual motifs": https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12827715/
- DreamSim: https://arxiv.org/html/2306.09344v3 · https://github.com/ssnl/dreamsim
- AI Co-Artist (GLSL): https://arxiv.org/abs/2512.08951
- tldraw Make Real / agents on canvas: https://ai.engineer/talks/agents-on-the-canvas-in-tldraw
- Figma – canvas open to agents: https://www.figma.com/blog/the-figma-canvas-is-now-open-to-agents/ · Figma Make: https://developers.figma.com/docs/code/intro-to-figma-make/
- Figma Weave: https://about.getcoai.com/news/figma-acquires-weavy-rebrands-as-figma-weave-for-node-based-ai-design
- Kling canvas: https://kr-asia.com/kling-ai-rolls-out-new-features-to-streamline-generative-content-workflows · https://beeble.ai/updates/2026-08-11-kling-3-omni
- Flora Series A: https://techcrunch.com/2026/01/27/node-based-design-tool-flora-raises-42m-from-redpoint-ventures/
- Recraft V4: https://www.abduzeedo.com/recraft-v4-brings-design-taste-and-native-svg-ai-generation · pricing: https://www.recraft.ai/docs/api-reference/pricing
- Adobe Firefly Text to Vector: https://helpx.adobe.com/firefly/generate-vectors/text-to-vector/generate-vectors-using-text-prompts.html
- Poppy AI: https://webcatalog.io/apps/poppy-ai
- 21st.dev / shadcn registries: https://21st.dev/blog/shadcn-registry-directory · https://noqta.tn/en/news/shadcn-github-registries-code-sharing-2026
- Anthropic pricing: https://docs.claude.com/en/docs/about-claude/pricing · vision token formula: https://platform.claude.com/docs/en/build-with-claude/vision
- Gemini pricing: https://llmgateway.io/models/gemini-3.1-flash-image · https://pricepertoken.com/pricing-page/model/google-gemini-3.1-flash-lite
