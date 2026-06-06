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

**InnerSpace** is a private, offline-first cognitive journal and reflection companion designed to run on resource-constrained edge devices. By utilizing the lightweight **`openbmb/MiniCPM5-1B-SFT`** model, InnerSpace extracts emotional sentiment, maps key life categories, flags potential cognitive distortions, and prompts self-reflection using Cognitive Behavioral Therapy (CBT) principles.

GitHub Repository: [awilliams88/innerspace](https://github.com/awilliams88/innerspace)
Hugging Face Space: [build-small-hackathon/innerspace](https://huggingface.co/spaces/build-small-hackathon/innerspace)

---

## 🧠 Core Features

* **Calming Mindful Interface**: A customized, premium dark-slate/violet visual dashboard optimized for reflection.
* **CBT Reflector Coach**: Engages the writer with open-ended, therapeutic prompts to explore underlying thoughts.
* **Cognitive Distortion Scanner**: Highlights thinking patterns like *Catastrophizing*, *All-or-Nothing Thinking*, or *Should Statements* to raise cognitive awareness.
* **Hybrid Inference**: Run locally on CUDA GPU (ZeroGPU space) with serverless API fallbacks.

---

## ⚙️ Application Workflow Guidelines

The application is built around single-responsibility layers following SOLID principles:

```text
+-----------------------+
|  Gradio UI (ui.py)    | <--- Renders dark-violet dashboard, text box, file uploads
+-----------+-----------+
            |
            v
+-----------+-----------+
| Core Facade (core.py) | <--- Unified API Router exposing analyze_journal_ui
+-----------+-----------+
            |
            v
+-----------+-----------+
| Analyzer (analyzer.py)| <--- Orchestrates the diary parsing & prompt generation
+-----+-----+-----+-----+
      |     |     |
      |     |     +-------------------------+
      |     |                               |
      v     v                               v
+-----+-----+-----+                 +-------+-------+
| Inference Engine|                 | Parser Engine |
| (inference.py)  |                 |  (parser.py)  |
|                 |                 |               |
| - Local bf16    |                 | - Text/MD     |
| - ZeroGPU A10G  |                 | - Section     |
| - HF API Client |                 |   Splitting   |
+-----------------+                 +---------------+
```

1. **User Input**: The user writes a journal entry in the writing block or uploads a `.txt`/`.md` entry.
2. **Core Routing**: The click event invokes `analyze_journal_ui` through [core.py](core.py).
3. **Model Generation**: The prompt is processed by the 1.2B parameter OpenBMB model in `inference.py`. It runs on a GPU locally when available.
4. **API Fallback**: If the local GPU/CPU is busy or unavailable, the system transparently falls back to the Hugging Face Serverless API.
5. **Error Handling**: If both inference paths fail (e.g., completely offline with no token), the system returns structured analysis-unavailable error indicators in the dashboard.

---

## 🚀 Modal.com Fine-Tuning Guide

Fine-tuning small models locally is difficult due to massive VRAM requirements. We resolve this by using **Modal.com**—a serverless cloud compute service that lets you run code on high-performance GPUs (like A10G or A100) on-demand, charging only for the exact seconds the GPU is active.

We have included a complete training script, [tune_journal.py](tune_journal.py), which performs **QLoRA (Quantized Low-Rank Adaptation)** to teach `openbmb/MiniCPM5-1B-SFT` how to identify reflections and CBT structures.

### Step-by-Step Training Guide

#### 1. Setup your Modal Account
1. Go to [Modal.com](https://modal.com/) and sign up for an account.
2. Install the Modal Python SDK on your machine (it is listed in our requirements file):
   ```bash
   pip install modal
   ```
3. Authenticate your local machine with the Modal environment:
   ```bash
   modal token set
   ```
   This will open a browser window to link your local CLI to your Modal billing and workspace.

#### 2. Create your Hugging Face Secret on Modal
To push the fine-tuned model back to your Hugging Face account, you need to store your write-access token securely on Modal:
1. Navigate to your Modal Dashboard -> **Secrets**.
2. Click **Create Secret** -> Choose **Hugging Face** template (or Custom).
3. Name the secret `my-huggingface-secret`.
4. Add the key: `HF_TOKEN` and set the value to your Hugging Face Access Token (User Access Token with Write permission).

#### 3. Run the Fine-Tuning Script
Run the script using the Modal runner. The command below tells Modal to upload the script, build the remote container, allocate an NVIDIA A10G GPU, mount a persistent volume, and begin training:
```bash
modal run tune_journal.py
```

#### 4. What the Script Does under the Hood
* **Container Creation**: Modal builds a cloud container image containing PyTorch, Hugging Face `transformers`, `peft`, `trl` (SFTTrainer), and `bitsandbytes` automatically.
* **Quantization (QLoRA)**: The base model is loaded in **4-bit precision (NF4)**. This allows a 1.2B parameter model to fit comfortably in a fraction of GPU memory, reducing costs.
* **LoRA Target Modules**: The script injects Low-Rank adapters into the attention layers (`q_proj`, `v_proj`, etc.). Only 0.5% of the model parameters are trained, protecting the model from forgetting concepts.
* **Checkpoint Volume**: Training outputs are saved to a persistent cloud disk volume named `inner-space-checkpoints` so you do not lose progress if the run terminates.
* **Push to Hub**: If the secret is set, it pushes the completed adapters directly to the HF repository (`build-small-hackathon/inner-space-1b-sft-cbt`).

---

## 🛠️ Codebase Architecture

The project directory contains:
- [app.py](app.py) - Launch and hosting configurations.
- [config.py](config.py) - Central settings and repo URLs.
- [core.py](core.py) - API Facade re-exporting key entry points.
- [analyzer.py](analyzer.py) - Analysis orchestrator and ZeroGPU wrapper.
- [inference.py](inference.py) - Lazy model loader and local/remote text generators.
- [parser.py](parser.py) - IO reader and section separator.
- [ui.py](ui.py) - Gradio block layout and interaction hooks.
- [styles.py](styles.py) - Calming violet custom styling overrides.
- [tune_journal.py](tune_journal.py) - Modal fine-tuning script.
- [requirements.txt](requirements.txt) - Dependency catalog.
- [run.sh](run.sh) - Local utility script for setup, formatting, linting, and verifying.

---

## 🖥️ Local Run & Quality Verification

To set up environment dependencies locally:
```bash
./run.sh setup
```

To launch the Gradio development server:
```bash
./run.sh app
```

To run quality checks (Ruff formatting, Ruff linting, Pyright type check, and python compilation):
```bash
./run.sh verify
```
All python files are checked against Pyright and Ruff to ensure high code quality.
