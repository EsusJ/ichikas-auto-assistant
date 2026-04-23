---
name: iaa-template-resource-integration
description: Integrate reusable image template resources into the IAA repository through the standard resources-to-R.py pipeline. Use when Codex needs to turn a captured image patch into a formal template under `resources/`, add or update a `*.png.json` resource definition, run `tools/make_resources.py`, verify the generated prefab appears in `iaa/tasks/R.py`, or replace ad-hoc image path loading with generated `R.*` references.
---

# IAA Template Resource Integration

## Overview

Use this skill when the main job is not detector tuning itself, but wiring a reusable image asset into the repository's resource system.
In this repo, the standard flow is:

1. Put the source image under `resources/`.
2. Add or update the matching `*.png.json`.
3. Run `tools/make_resources.py` with the repo `.venv`.
4. Use the generated prefab from `iaa/tasks/R.py` in production code.

Do not add a second resource-loading path when this flow fits the task.

## When To Use A Formal Resource

Promote an image into a formal resource when:

- production code should reuse it beyond a one-off probe
- the code should load it through generated `R.py`
- the image is a stable UI template rather than temporary debug evidence
- future updates would benefit from having the template discoverable in `resources/`

Leave the image in `logs/` when:

- it is only for investigation
- the visual strategy is still unsettled
- the detector may switch away from templates entirely

## Workflow

1. Confirm the image should become a formal template, not just a debug artifact.
2. Save the exact source image under the correct `resources/<variant>/...` folder.
3. Add or update the corresponding `*.png.json`.
4. Run `.\.venv\Scripts\python.exe tools\make_resources.py`.
5. Inspect the generated entry in `iaa/tasks/R.py`.
6. Update business code to use the generated `R.*` prefab instead of manual paths.
7. Re-run a focused verification against the real samples or task code.

## Resource Placement

- Prefer the closest existing domain folder under `resources/jp/...` unless the task clearly belongs elsewhere.
- Follow the repo's current naming style for neighboring files.
- If the template is tied to a specific page or feature, keep it near the related screen resources rather than creating a vague catch-all folder.

## Meta File Guidance

- Match each source image with a `*.png.json` file beside it.
- Prefer the same resource schema style that already works with this repository's `R.py` generation flow.
- Reuse neighboring resource files as the first source of truth for naming and structure.
- If the project is using generated `R.py` with variants enabled, verify the chosen meta format actually survives the full `tools/make_resources.py` pipeline before committing to it.

## Generation And Verification

- Always run the generator with the repo virtual environment:
  `.\.venv\Scripts\python.exe tools\make_resources.py`
- Treat generator failure as a workflow problem to resolve before changing more business code.
- After generation, verify:
  - the expected cut image exists under `iaa/res/`
  - the prefab appears in `iaa/tasks/R.py`
  - production code reads from `R.*.template.file_path` or the generated prefab object, not from `resources/...` directly

## Code Integration Rules

- Prefer `from . import R` or the local repo convention for accessing generated resources.
- Do not hardcode project-root-relative `resources/...` paths in business code when a generated prefab exists.
- Keep resource loading thin: if all you need is the generated template path, read it from `R.*`.

## Guardrails

- Use the repo `.venv` for generation and validation scripts.
- Do not hand-edit `iaa/tasks/R.py`; it is generated.
- Do not leave a new template half-integrated. If the template is formalized, regenerate resources and switch code to the generated reference in the same change.
- If generation fails because of repository-level meta constraints, stop and immediately prompt the user about the failure and the reason, rather than bypassing and using alternative methods.
