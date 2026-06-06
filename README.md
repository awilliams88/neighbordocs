---
title: InnerSpace
emoji: 🧠
colorFrom: purple
colorTo: gray
sdk: gradio
sdk_version: 6.16.0
app_file: app.py
python_version: "3.12"
short_description: Privacy-first offline cognitive journal & reflection coach
pinned: false
---

# InnerSpace

**InnerSpace** is a private, offline-first cognitive journal and AI reflection companion. It runs a fine-tuned 1.2B parameter language model directly on the device — no data ever leaves the session.

The model analyzes journal entries through the lens of **Cognitive Behavioral Therapy (CBT)**: surfacing emotions, identifying affected life areas, flagging cognitive distortions, and responding with a gentle reflective question to help the writer think more clearly.

**Live Space**: [build-small-hackathon/innerspace](https://huggingface.co/spaces/build-small-hackathon/innerspace)
**Source Code**: [awilliams88/innerspace](https://github.com/awilliams88/innerspace)
**Fine-tuned Model**: [build-small-hackathon/inner-space-1b-sft-cbt](https://huggingface.co/build-small-hackathon/inner-space-1b-sft-cbt)

---

## What It Does

Write or upload a journal entry (`.txt` or `.md`). InnerSpace will return a structured reflection in four parts:

| Section | Description |
|---|---|
| **Emotions** | Dominant emotional states present in the entry |
| **Life Areas** | Affected domains — career, relationships, health, etc. |
| **Cognitive Distortions** | Patterns like *Catastrophizing*, *Mind Reading*, or *All-or-Nothing Thinking* |
| **Reflection** | A gentle open-ended question to prompt deeper self-awareness |

---

## Fine-Tuned Model

The inference engine is powered by a **QLoRA-adapted** version of [`openbmb/MiniCPM5-1B-SFT`](https://huggingface.co/openbmb/MiniCPM5-1B-SFT), trained specifically on CBT reflection patterns.

**Why fine-tune instead of prompting?**
The base model is general-purpose. Fine-tuning teaches it the exact four-section output structure (Emotions / Life Areas / Cognitive Distortions / Reflection) and CBT vocabulary — producing more consistent, therapeutically-grounded responses without relying on long system prompts.

**Training details:**
- Method: QLoRA (4-bit NF4 quantization + LoRA adapters on attention layers)
- Hardware: NVIDIA A10G GPU via [Modal.com](https://modal.com)
- Dataset: 9 synthetic CBT journal entries covering career anxiety, relationship stress, health anxiety, and imposter syndrome
- Steps: 50 (token accuracy improved from ~44% → ~85%)
- Adapter size: 4.15 MB (only 0.19% of total parameters trained)

The fine-tuned LoRA adapter is published at [`build-small-hackathon/inner-space-1b-sft-cbt`](https://huggingface.co/build-small-hackathon/inner-space-1b-sft-cbt) and is loaded automatically on top of the base model at Space startup.

---

## Inference Architecture

```
User Input (text or file)
        │
        ▼
┌─────────────────────┐
│    Gradio UI        │  ui.py — dark-violet mindful dashboard
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Core Facade      │  core.py — unified entry point
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Analyzer           │  analyzer.py — prompt construction & ZeroGPU dispatch
└──────────┬──────────┘
           │
     ┌─────┴──────┐
     ▼            ▼
┌─────────┐  ┌──────────┐
│Inference│  │  Parser  │  inference.py — model execution
│ Engine  │  │  Engine  │  parser.py — file reading & section splitting
└────┬────┘  └──────────┘
     │
     ├── ZeroGPU (primary): base model + LoRA adapter via PeftModel
     └── HF Serverless API (fallback): base model via InferenceClient
```

**Inference priority:**
1. **ZeroGPU** — loads `MiniCPM5-1B-SFT` in bfloat16 and applies the fine-tuned LoRA adapter via `PeftModel`. Runs on an NVIDIA A10G in the Space.
2. **HF Serverless API** — transparent fallback if the GPU allocation fails or is unavailable.
3. **Error** — if both paths fail, the UI returns a clear error message. No silent failures.

---

## Example Entries

The [`examples/`](examples/) directory contains ready-to-load journal entries covering common scenarios. Use the **Load Example** buttons in the UI to try them directly.

---

## Local Development

**Setup:**
```bash
./run.sh setup
```

**Run locally:**
```bash
./run.sh app
```

**Quality checks** (Ruff formatting, Ruff linting, Pyright type checking, Python compilation):
```bash
./run.sh verify
```

---

## Codebase

| File | Purpose |
|---|---|
| `app.py` | Gradio launch entry point |
| `config.py` | Central constants — model IDs, repo URLs, limits |
| `core.py` | Public API facade |
| `analyzer.py` | Journal analysis orchestrator with ZeroGPU decorator |
| `inference.py` | Lazy model loader — applies LoRA adapter, handles fallback |
| `parser.py` | File reader and section splitter |
| `ui.py` | Gradio layout, components, and event hooks |
| `styles.py` | Custom dark-violet CSS theme |
| `tune.py` | QLoRA fine-tuning script (Modal.com) |
| `requirements.txt` | Python dependencies |
| `run.sh` | Local dev utility |

---

## Tech Stack

- **Model**: `openbmb/MiniCPM5-1B-SFT` + custom LoRA adapter (`build-small-hackathon/inner-space-1b-sft-cbt`)
- **Fine-tuning**: QLoRA via `peft` + `trl` SFTTrainer on Modal A10G
- **Inference**: `transformers` + `peft` (PeftModel) + `accelerate`
- **UI**: Gradio 6 with custom CSS
- **Hosting**: Hugging Face Spaces (ZeroGPU)
- **Sponsor**: [OpenBMB](https://github.com/OpenBMB) — MiniCPM model family