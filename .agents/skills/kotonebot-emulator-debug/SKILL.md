---
name: kotonebot-emulator-debug
description: Debug live game UI automation through kotonebot and the emulator. Use when Codex needs to connect to MuMu, initialize kotonebot context, control the device, capture screenshots, save runtime artifacts, write one-off probe scripts, or investigate why a recognition/click/switch flow behaves incorrectly on a real page.
---

# Kotonebot Emulator Debug

## Overview

Use this skill for live debugging against the emulator, not for static code review alone.
Prefer reproducible probe scripts over ad-hoc shell poking so you can save artifacts under `logs/` and compare states across frames.
For deep ROI / HSV / mask / contour analysis, pair this skill with `kotonebot-vision-debug`.

## Workflow

1. Reproduce the issue on the current emulator page before changing code.
2. Connect to the emulator through kotonebot using the repo virtualenv and the same context init path used by the project.
3. Capture a baseline screenshot and the parsed state before touching the UI.
4. Write a small inline Python probe that performs one narrow investigation:
   - dump current state
   - click a specific control
   - poll for a few frames
   - save raw screenshots
   - save annotated screenshots if visual explanation helps
5. Compare multiple states side by side before deciding whether the bug is in:
   - page recognition
   - active-state recognition
   - click target selection
   - wait/poll timing
   - page transition assumptions
6. Only after the failure mode is clear, patch the implementation and rerun the same probe.

## Connect And Run

Prefer the repo virtualenv:

```powershell
.\.venv\Scripts\python.exe -m iaa.game_ui.side_tabbar
```

For one-off probes, use inline Python with the same setup pattern:

```python
from pathlib import Path
import json
from kotonebot.backend.context.context import init_context, manual_context
from kotonebot.client.host import Mumu12V5Host
from kotonebot.client.host.mumu12_host import MuMu12HostConfig
from iaa.config.base import IaaConfig

config = IaaConfig.model_validate(json.loads(Path("conf/default.json").read_text(encoding="utf-8")))
host = Mumu12V5Host.list()[0]
if not host.running() and config.game.check_emulator:
    host.start()
    host.wait_available()

device = host.create_device("nemu_ipc", MuMu12HostConfig())
device.orientation = "landscape"
init_context(target_device=device, force=True)

with manual_context("manual"):
    ...
```

## Probe Script Patterns

Use short, disposable scripts for each question instead of one giant debug program.

### Save raw screenshots

- Save the unmodified frame first.
- Put outputs under a dedicated folder such as `logs/side_tabbar_switch_raw`.
- Name files by sequence and state, for example `00_initial.png`, `01_after_click0.png`.

### Save annotated screenshots

- Draw only the overlays needed to explain the hypothesis.
- Typical overlays:
  - container rect
  - tab rects
  - click centers
  - detected active rect
  - score text per candidate
- Save annotated outputs in a sibling folder such as `logs/side_tabbar_switch_marked`.

### Poll state transitions

- After a click, capture several frames instead of trusting a single delayed read.
- Use a longer first wait and shorter follow-up polls.
- Print both parsed state and low-level measurements for each poll.

### Measure instead of guessing

When debugging vision logic, print numeric evidence:

- contour bounding boxes
- contour areas
- per-tab color ratios
- connected-component sizes
- badge counts

If two explanations compete, write a script that computes both and compare them on saved frames.

## Debugging Heuristics

### Click problems

- Verify the click point on the screenshot before changing retry logic.
- Distinguish:
  - click lands on wrong target
  - click lands correctly but page state is read too early
  - click succeeds but recognition interprets the new frame incorrectly

### Recognition problems

- Separate tab discovery from active-tab recognition.
- If a global color contour merges multiple tabs, score each tab within its own rect instead of relying on one large connected region.
- If counts change across frames, determine whether the UI truly changed or only the recognition drifted.

### Current-page assumptions

- Do not assume the sidebar structure changed just because indices drifted.
- Save screenshots for each active state and confirm visually.
- State conclusions only after comparing raw images, not from logs alone.

## File And Logging Conventions

- Keep all temporary debugging artifacts under `logs/`.
- Use one folder per investigation.
- Prefer raw and annotated outputs in separate folders.
- Keep filenames sortable with numeric prefixes.

## Patch And Verify

After identifying the bug:

1. Make the smallest code change that matches the proven failure mode.
2. Re-run the same probe first.
3. Re-run the module entry point or the task flow that originally failed.
4. If the fix changes recognition logic, verify at least one additional state or page so the fix is not overfit to a single screenshot.
5. If the page is scrollable or stateful, treat cross-state validation as required rather than optional:
   - current frame
   - small scroll or page transition
   - return / reverse transition
6. A single good frame is not enough evidence for a vision fix.

## Guardrails

- Prefer live evidence over intuition.
- Prefer raw screenshots over only `imshow`.
- Prefer one-purpose scripts over reusable abstractions during investigation.
- Do not claim the UI structure changed until screenshots confirm it.
- If a helper is only for a single investigation, keep it out of production code.
