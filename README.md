# NeighborDocs

NeighborDocs is a document helper for everyday paperwork.

## What it does

- Accepts a document upload and optional notes.
- Extracts text from PDFs when available.
- Produces a short plain-English summary and next-step checklist.

## Local setup

```bash
./run.sh setup
./run.sh
```

## Quality checks

```bash
./run.sh verify
```

## Files

- `app.py` - Gradio app entrypoint.
- `verify_code.py` - formatter, lint, and test wrapper.
- `run.sh` - setup and launch script.
- `requirements.txt` - runtime dependencies.

