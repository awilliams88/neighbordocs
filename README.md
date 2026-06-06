---
title: NeighborDocs
emoji: 📄
colorFrom: blue
colorTo: gray
sdk: gradio
sdk_version: 6.16.0
app_file: app.py
python_version: "3.12"
short_description: Plain-English help for everyday paperwork
pinned: false
---

# NeighborDocs

NeighborDocs is a practical document helper for everyday paperwork: bills,
school notices, receipts, forms, reports, and other documents that people often
need to understand quickly.

GitHub repo: [awilliams88/neighbordocs](https://github.com/awilliams88/neighbordocs)

## What it does

- Accepts a PDF, TXT, or MD upload plus optional user notes.
- Extracts readable text from the first pages of a PDF.
- Lets the user choose a sponsor-aligned model strategy.
- Shows an extracted-text preview.
- Produces a plain-English summary and next-step checklist.

## Hackathon fit

Track: Backyard AI.

Why this project exists: many useful AI tools should help with small, everyday
problems. NeighborDocs focuses on making ordinary paperwork easier to understand
without needing a large model.

Award surfaces:

- Backyard AI: direct real-world usefulness.
- NVIDIA / document intelligence: planned parser and document extraction path.
- Tiny Titan: planned small-model summarization and checklist generation path.
- Best Demo: clear before/after document workflow.
- OpenAI / Codex: built and maintained with Codex; GitHub history is preserved.

## Models and planned integrations

| Model or tool | Role | Status | Parameter count |
| --- | --- | --- | --- |
| `pypdf` | Basic PDF text extraction | Active | Not a model |
| `nvidia/NVIDIA-Nemotron-Parse-v1.1` | Layout-aware PDF/PPT extraction | Recommended path | <1B |
| Small text reasoner | Summary, obligations, deadlines, next actions | Planned | <=4B target |
| `openbmb/MiniCPM-V-4.6` | Scanned-image/document understanding | Candidate | 1B class |
| Cohere tiny multilingual LLM family | Translation and local-language explanation | Candidate | 3.3B class |

The final model list will stay within the hackathon rule that every model must
be under 32B total parameters. The first planned sponsor path is NVIDIA
Nemotron Parse because document extraction is central to the product.

## Architecture

```text
Upload + notes
  -> file type router
  -> sponsor model strategy selector
  -> PDF/text extraction
  -> extracted text preview
  -> model or rule-based document interpreter
  -> plain-English summary + next steps
```

Key files:

- `app.py` - thin Gradio launch entry point.
- `src/neighbordocs/config.py` - app constants, URLs, and model plan.
- `src/neighbordocs/core.py` - document extraction and analysis logic.
- `src/neighbordocs/ui.py` - Gradio layout and event wiring.
- `examples/` - sample demo documents for judges and screenshots.
- `requirements.txt` - runtime dependencies.
- `run.sh` - setup, lint, format, verify, and local app launch.

## Local setup

```bash
./run.sh setup
./run.sh
```

## Quality checks

```bash
./run.sh verify
```

`verify` runs Ruff format checks, Ruff lint, and Python compile checks using
default Ruff rules. The project intentionally does not include a default test
suite while the hackathon apps are being built quickly.

## Deployment

The Hugging Face Space is published under the Build Small Hackathon org:

[build-small-hackathon/neighbordocs](https://huggingface.co/spaces/build-small-hackathon/neighbordocs)

## Submission checklist

- Hugging Face Space: created.
- GitHub repo: [awilliams88/neighbordocs](https://github.com/awilliams88/neighbordocs).
- Demo video: pending.
- Social post: pending.
- Final model list and parameter counts: pending once model integrations are
  selected.

## Current limitations

- OCR for scanned images is not implemented yet.
- The summary is currently a rule-based MVP response, not a final model output.
- Multilingual output is planned but not implemented yet.
