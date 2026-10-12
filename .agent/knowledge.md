# Verified Knowledge

### Render-in-the-Loop beats more training data

- **Fact:** A model trained on 0.85M samples with visual feedback beat OmniSVG and InternSVG (trained on 16M) at SVG generation.
- **Source:** Render-in-the-Loop (2026) https://arxiv.org/abs/2604.20730
- **Verified:** 2026-09-29
- **Notes:** The model sees the canvas rendered so far before adding each shape. Also uses "Render-and-Verify" at inference to filter broken/duplicate shapes.

---

### Autonomous image generation loops converge to generic output

- **Fact:** Text-to-image-to-text loops (SDXL + LLaVA) converge to ~12 generic "commercially safe" motifs across all tested configurations. The authors call it "visual elevator music."
- **Source:** Hintze et al. (2025) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12827715/
- **Verified:** 2026-09-29
- **Notes:** 700 runs, 100 rounds each. Held across model pairs, temperatures, longer prompts. This means the loop MUST re-anchor against user references every round.

---

### LLM SVG quality degrades with complexity

- **Fact:** SVGenius benchmark (22 models) found every model gets worse as SVG complexity rises. Style transfer is the hardest task. Reasoning-focused training helped more than model size.
- **Source:** SVGenius https://arxiv.org/abs/2506.03139
- **Verified:** 2026-09-29
- **Notes:** Proprietary models beat open-source. Implication: keep assets simple (icons, logos, spot illustrations), use named primitives not raw paths.

---

### LLMs do better with higher-level formats than raw SVG

- **Fact:** VGBench found LLMs perform much better with TikZ and Graphviz than with low-level SVG path data.
- **Source:** VGBench https://arxiv.org/abs/2407.10972
- **Verified:** 2026-09-29
- **Notes:** Suggests using a higher-level intermediate form (named shapes, groups, parameters) compiled to SVG.

---

### Cost model for iteration budget

- **Fact:** Haiku 4.5 with edits + cached context: ~$0.006-0.01/iter (~$0.12-0.20 for 20 iters). Full rewrite: ~$0.024/iter (~$0.48 for 20). Gemini Flash-Lite full rewrite: ~$0.007/iter (~$0.14 for 20). Adding image generation per round adds ~$0.80 for 20 rounds.
- **Source:** docs/research.md cost model, Anthropic pricing docs, Gemini pricing
- **Verified:** 2026-09-29
- **Notes:** Edits + caching are the two biggest cost levers. Generate raster targets at most 1-2 times, not every round.

---

### DreamSim beats CLIP/LPIPS for visual similarity

- **Fact:** DreamSim (trained on ~20k human judgments) matches human similarity ratings better than LPIPS, CLIP, or DINO for evaluating "does this match my reference."
- **Source:** DreamSim https://arxiv.org/html/2306.09344v3
- **Verified:** 2026-09-29
- **Notes:** Pixel metrics (SSIM) miss layout/pose/meaning differences. A rough sketch is not a picture of the target, so no single metric fits. Suggested: edge IoU for structure, DreamSim for style, VLM judge for structured feedback.

---

### Recraft is the direct SVG competitor

- **Fact:** Recraft V3 Vector API costs $0.08 per SVG. Text-to-native-SVG with editable paths. One-shot from a prompt, no sketch input, no iterative loop.
- **Source:** https://www.recraft.ai/docs/api-reference/pricing
- **Verified:** 2026-09-29
- **Notes:** V4/V4.1 released Feb and May 2026. The differentiator is the loop + sketch input, not raw SVG quality.

---

### SVG filter 3D capabilities and limits

- **Fact:** SVG feSpecularLighting/feDiffuseLighting provide Phong lighting via alpha-channel bump maps. Sufficient for: soft shadows, specular highlights, emboss, frosted glass, metallic surfaces. Cannot do: true refraction, ray tracing, subsurface scattering, multi-bounce lighting, perspective-correct textures.
- **Source:** MDN docs, W3C SVG spec, prototype testing
- **Verified:** 2026-09-29
- **Notes:** Single light per filter primitive. Multiple lights = multiple stacked filters = verbose and slow. The crossover to WebGL: refraction, caustics, volumetric effects, PBR, animated lighting.

---

### Shutterstock/Getty market data (corrected)

- **Fact:** Shutterstock FY2025: $989.9M total revenue (+6%, not +16%). Content revenue: $786.7M (+4%). Getty FY2025: $981.3M (+4.5%). Creative revenue: $556.9M (+0.7%). Combined creative/content: ~$1.34B. Getty abandoned $3.7B Shutterstock merger Jul 1 2026 after UK CMA demanded divestiture.
- **Source:** Shutterstock SEC filing, Getty earnings release, Yahoo Finance
- **Verified:** 2026-09-29
- **Notes:** The draft application incorrectly stated 16% growth (that was Data/Distribution segment only). The "~$2B" claim includes editorial and data licensing — creative-only is ~$1.34B.

---

### Competitors are closer than claimed

- **Fact:** Figma (Make + canvas agents + Weave), tldraw (Make Real + agents on canvas), Recraft (native SVG), Adobe (Firefly Text to Vector), Flora ($42M Series A), Krea, and 21st.dev (shadcn registries) all overlap with parts of this idea.
- **Source:** docs/research.md competitive landscape
- **Verified:** 2026-09-29
- **Notes:** "Incumbents won't build this" is weak. Defensible framing: nobody owns the finished atomic asset that's exportable, editable, and code-ready. Competitors produce whole apps OR raw media, not single reusable components.
