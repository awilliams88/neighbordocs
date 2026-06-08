---
title: InnerSpace
emoji: 🧠
colorFrom: purple
colorTo: gray
sdk: gradio
sdk_version: 6.17.3
app_file: app.py
python_version: "3.12"
short_description: Local-first cognitive journal & reflection coach
pinned: false
---

# Inner 🧠 Space

**InnerSpace** is a private, local-first cognitive journal and AI reflection companion. It runs a fine-tuned 1.2B parameter language model inside the Hugging Face Space runtime. There is no serverless inference fallback, so journal text is not sent to an external inference API.

The model analyzes journal entries through the lens of **Cognitive Behavioral Therapy (CBT)**: surfacing emotions, identifying affected life areas, flagging cognitive distortions, and responding with a gentle reflective question to help the writer think more clearly.

InnerSpace is a reflective journaling tool, not medical advice, diagnosis, crisis counseling, or a replacement for a licensed mental-health professional. If someone may be in immediate danger or crisis, they should contact local emergency services or a crisis hotline.

### Links

- **Demo**: [Video](Demo.mp4)
- **Social Post**: [LinkedIn](https://www.linkedin.com/posts/awilliams1988_buildsmall-huggingface-ai-ugcPost-7469692012166893568-T16Y)
- **Github Repo**: [awilliams88/innerspace](https://github.com/awilliams88/innerspace)
- **Hugging Space**: [build-small-hackathon/innerspace](https://huggingface.co/spaces/build-small-hackathon/innerspace)
- **Fine-tuned Model**: [build-small-hackathon/inner-space-1b-sft-cbt](https://huggingface.co/build-small-hackathon/inner-space-1b-sft-cbt)

## What It Does

Write or upload a journal entry (`.txt` or `.md`) and set your current distress level. InnerSpace will return a structured reflection in six parts:

| Section | Description |
|---|---|
| **Emotions** | Dominant emotional states present in the entry |
| **Life Areas** | Affected domains — career, relationships, health, etc. |
| **Cognitive Distortions** | Patterns like *Catastrophizing*, *Mind Reading*, or *All-or-Nothing Thinking* |
| **Balanced Reframe** | A grounded alternative interpretation that does not dismiss the writer's feelings |
| **Tiny Next Step** | One realistic action the writer can try in the next 10 minutes |
| **Reflection** | A gentle open-ended question to prompt deeper self-awareness |

---

## Fine-Tuned Model

The inference engine is powered by a **QLoRA-adapted** version of [`openbmb/MiniCPM5-1B-SFT`](https://huggingface.co/openbmb/MiniCPM5-1B-SFT), trained specifically on CBT reflection patterns.

**Why fine-tune instead of prompting?**
The base model is general-purpose. Fine-tuning teaches it the core CBT output structure and vocabulary — producing more consistent, therapeutically-grounded responses without relying on long system prompts. The current app extends that flow with a balanced reframe, a tiny next step, and distress-level context.

**Training details:**
- Method: QLoRA (4-bit NF4 quantization + LoRA adapters on attention layers)
- Hardware: NVIDIA A10G GPU via [Modal.com](https://modal.com)
- Dataset: 17 structured CBT journal entries plus 19 multi-turn follow-up coaching examples (including off-topic deflection and redirection)
- Output format: six sections aligned with the app UI — emotions, life areas, cognitive distortions, balanced reframe, tiny next step, and reflection
- Follow-up behavior: brief second-turn coaching for self-critical replies without hidden reasoning tags or business-style metrics
- Steps: 220 with a rank-16 LoRA adapter and 1536-token examples

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
     └── ZeroGPU / local runtime: base model + LoRA adapter via PeftModel
```

**Inference priority:**
1. **ZeroGPU** — loads `MiniCPM5-1B-SFT` in bfloat16 and applies the fine-tuned LoRA adapter via `PeftModel`. Runs on an NVIDIA A10G in the Space.
2. **Privacy-first failure policy** — if local inference fails, the app returns a clear error instead of routing journal text to a serverless API.
3. **Error** — if local execution fails, the UI returns a clear error message. No silent failures.

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
This launches through `app.py` so Gradio receives the custom theme and CSS.

**Quality checks** (Ruff formatting, Ruff linting, Pyright type checking, Python compilation):
```bash
./run.sh verify
```

---

## Codebase

### Root
| File | Purpose |
|---|---|
| `app.py` | Gradio launch entry point |

### `env/` — App infrastructure
| File | Purpose |
|---|---|
| `env/config.py` | Central constants — model IDs, repo URLs, limits |
| `env/runtime.py` | Env var loader and asyncio cleanup patch |

### `core/` — Business logic
| File | Purpose |
|---|---|
| `core/analyzer.py` | Journal analysis orchestrator with ZeroGPU decorator |
| `core/inference.py` | Lazy model loader — applies LoRA adapter, runs local inference |
| `core/parser.py` | File reader and CBT section splitter |

### `ui/` — Presentation
| File | Purpose |
|---|---|
| `ui/layout.py` | Gradio layout, components, and event hooks |
| `ui/styles.py` | Custom dark-violet CSS theme |

### `modal/` — Remote fine-tuning
| File | Purpose |
|---|---|
| `modal/tune.py` | QLoRA fine-tuning orchestrator (Modal.com) |
| `modal/dataset.py` | CBT training dataset and prompt builders |
| `modal/CARD.md` | Hugging Face model card for the LoRA adapter |

### Project files
| File | Purpose |
|---|---|
| `requirements.txt` | Python dependencies |
| `run.sh` | Local dev utility — setup, verify, launch |

---

## Tech Stack

- **Model**: `openbmb/MiniCPM5-1B-SFT` + custom LoRA adapter (`build-small-hackathon/inner-space-1b-sft-cbt`)
- **Fine-tuning**: QLoRA via `peft` + `trl` SFTTrainer on Modal A10G
- **Inference**: `transformers` + `peft` (PeftModel) + `accelerate`
- **UI**: Gradio 6 with custom CSS
- **Hosting**: Hugging Face Spaces (ZeroGPU)
- **Sponsor**: [OpenBMB](https://github.com/OpenBMB) — MiniCPM model family

---