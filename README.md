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

Current MVP:

- `pypdf` for basic PDF text extraction.
- Rule-based placeholder summary while model integrations are added.

Planned model path:

- NVIDIA Nemotron Parse or a comparable small document parser for layout-aware
  extraction.
- A small reasoning model under the 32B hackathon limit for summarization,
  action extraction, and checklist generation.
- Optional multilingual helper model for simple translation or local-language
  explanation.
- Modal compute may be used for heavier parsing or model experiments using the
  hackathon Modal credits.

All model choices will stay within the hackathon rule that every model must be
under 32B total parameters.

## Architecture

```text
Upload + notes
  -> file type router
  -> PDF/text extraction
  -> extracted text preview
  -> model or rule-based document interpreter
  -> plain-English summary + next steps
```

Key files:

- `app.py` - Gradio UI, upload handling, extraction, and response generation.
- `requirements.txt` - Hugging Face Space runtime dependencies.
- `requirements-dev.txt` - local development and verification dependencies.
- `run.sh` - setup, format, test, verify, and local app launch.
- `verify_code.py` - formatter, linter, and test wrapper.

## Local setup

```bash
./run.sh setup
./run.sh
```

## Quality checks

```bash
./run.sh verify
```

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
- The summary is currently a scaffolded MVP response, not a final model output.
- Multilingual output is planned but not implemented yet.
