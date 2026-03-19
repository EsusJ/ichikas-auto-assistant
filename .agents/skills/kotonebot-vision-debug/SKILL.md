---
name: kotonebot-vision-debug
description: Debug and refine kotonebot UI recognition logic. Use when Codex needs to analyze ROI choice, HSV thresholds, mask quality, morphology, contours, candidate scoring, cross-frame stability, or the visual semantics of what should be detected on game UI screenshots.
---

# Kotonebot Vision Debug

## Overview

Use this skill when the hard part is not connecting to the emulator, but understanding why a visual detector is selecting the wrong pixels, region, contour, or score.
Prefer saved-frame probes and side-by-side comparisons before patching production code.
If the outcome should become a formal reusable template under `resources/` and `iaa/tasks/R.py`, hand off to `iaa-template-resource-integration` after the visual strategy is clear.

## Core Principles

- First confirm that the algorithm is trying to detect the right visual object.
- Then confirm that the ROI is appropriate.
- Only then tune HSV bounds, morphology, scoring, or filters.
- For stable game UI, color semantics often have higher leverage than geometry tweaks.
- Use geometry and scoring to refine a good mask, not to rescue a bad mask.
- Do not turn every threshold into a public config by default. For stable pages, prefer class constants first and only promote a value to a configurable parameter after repeated, real usage proves it needs to vary.

## Workflow

1. Save the exact failing frame before touching code.
2. Save the relevant ROI patch, not just the whole screenshot.
3. Inspect the target semantically:
   - What pixels truly belong to the thing you want?
   - Is the detector looking for the same thing, or for a proxy such as an edge or contour?
4. Verify whether the search region is correct.
   - If the ROI is too large or semantically wrong, threshold tuning will optimize the wrong target.
   - If a small local `zone` exists, confirm it is actually better than searching the whole parent region.
5. Save intermediate stages for the current implementation.
6. If an alternative strategy exists, run both on the same frame and compare them side by side.
7. Only after the failure mode is clear, patch the implementation and rerun the same probe.

## What To Save

For vision bugs, do not stop at raw + final overlay.
Save the intermediate images that explain where the algorithm diverges:

- ROI patch
- raw mask
- morphology outputs such as `open` / `close`
- contour visualization
- final selected candidate

Save a companion text file with numeric evidence for the same frame:

- contour bounding boxes
- area / fill ratio
- aspect ratio
- candidate scores
- accept / reject reasons

A good default folder layout is:

- `00_raw.png`
- `01_roi.png`
- `02_mask_raw.png`
- `03_mask_open.png`
- `04_mask_close.png`
- `05_contours.png`
- `06_overlay.png`
- `07_metrics.txt`

When investigating one bad candidate, save its per-item intermediate artifacts in a dedicated folder instead of mixing them into page-level outputs.

## ROI Guidance

- Validate ROI choice before tuning thresholds.
- If the ROI is too big, unrelated bright or saturated regions may merge into the target.
- If the ROI is too small, morphology may hallucinate a shape from sparse fragments.
- If a detector already has a good parent region such as `item rect`, prefer testing whether the whole parent region is a better search scope than a hand-tuned sub-zone.

## Color Guidance

- If the page uses stable, stylized UI colors, start with color segmentation before edge-based heuristics.
- Ask whether white / non-white, low-saturation / high-value, or a stable accent color better represents the target.
- Tightening HSV bounds is often more valuable than adding more geometric filters when masks are bleeding across unrelated regions.
- If a bug looks like “two things got connected,” test stricter HSV bounds before adding a special-case contour rule.

## Morphology Guidance

- `open` removes small noise; `close` can also accidentally bridge separate regions.
- When a contour becomes too large, save `raw mask`, `open`, and `close` side by side to identify which stage created the bridge.
- If `close` is the step that merges regions, prefer:
  - weakening `close`
  - improving the mask
  - or constraining the candidate geometry
  before adding a special-case patch.

## Candidate Selection Guidance

- Distinguish algorithm-definition problems from parameter problems:
  - If the algorithm is detecting the wrong visual object, change the method.
  - If the algorithm is detecting the right object with unstable boundaries, then tune thresholds and morphology.
- Do not assume a higher score means a better target if the mask itself is wrong.
- If a switch or filter only made sense for the old detector, revisit or remove it after the method changes.

## Configuration Guidance

- Treat HSV bounds, morphology kernels, size thresholds, score weights, and similar detector knobs as implementation details unless there is a proven cross-page need to vary them.
- When experimenting, it is fine to temporarily expose a value for validation. After the behavior is understood, prefer folding the winning value back into a constant instead of leaving a long-lived config surface behind.
- A parameter should earn its way into the public API. Good reasons include:
  - multiple pages genuinely need different values
  - multiple callers already need to pass different values
  - the parameter changes the user-facing behavior rather than only detector internals
- “Maybe we might tune this later” is not enough reason to expose a config field.

## Comparison Probes

- When comparing two recognition strategies, do not patch production code first.
- Write a probe that runs both approaches on the same saved frame or live frame.
- Save side-by-side outputs for the current implementation and the candidate implementation.
- Use the same overlays and metrics where possible so differences are easy to inspect.
- Only switch production code after the probe shows a clear win.

## Verification

- A single good frame is not enough evidence for a vision fix.
- If the page is scrollable or stateful, verify at least:
  - current frame
  - small scroll or page transition
  - return / reverse transition
- When counts change across frames, determine whether the UI truly changed or only the recognition drifted.

## Guardrails

- Prefer saved evidence over intuition.
- Prefer one-purpose probes over generalized helpers during investigation.
- If the bug still looks ambiguous, save more intermediate visual evidence before changing another parameter.
- Do not preserve a stale parameter or filter just because it existed before the detector changed.
- Do not introduce ad-hoc resource loading when the repository already expects reusable templates to go through `resources/`, `tools/make_resources.py`, and generated `R.py` references.
