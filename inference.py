"""
Module responsible for model loading and text generation.
Handles local GPU/CPU execution and fallback to Hugging Face Serverless Inference API.
"""

from __future__ import annotations

import os
from typing import Any
import torch

from config import MODEL_ID

# Caches for the model and tokenizer to prevent re-loading on every call
_model: Any = None
_tokenizer: Any = None


def get_model_and_tokenizer() -> tuple[Any, Any]:
    """Loads and caches the Hugging Face model and tokenizer lazily."""
    global _model, _tokenizer
    if _model is None:
        from transformers import AutoModelForCausalLM, AutoTokenizer

        print(f"Loading tokenizer for {MODEL_ID}...")
        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            token=os.environ.get("HF_TOKEN"),
        )

        print(f"Loading model {MODEL_ID}...")
        # Select bfloat16 on CUDA devices, else float32 for CPU/MPS compatibility
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            dtype=dtype,
            low_cpu_mem_usage=True,
            token=os.environ.get("HF_TOKEN"),
        )

        # Move model to CUDA GPU memory if available
        if torch.cuda.is_available():
            print("Moving model to CUDA device...")
            _model = _model.to("cuda")

    return _model, _tokenizer


def run_model_inference(prompt: str) -> tuple[str, str]:
    """Executes inference using local hardware first, falling back to Serverless API on failure."""
    log_lines: list[str] = []
    try:
        log_lines.append("Initializing local model execution...")
        model, tokenizer = get_model_and_tokenizer()
        device = str(model.device)
        log_lines.append(f"Running local model execution on device: {device}...")

        # Format prompt according to the model's chat template structure
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        print("Generating response...")
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

        # Retrieve the generated assistant text block only (excluding the input prompt)
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        log_lines.append("Local model execution completed successfully.")
        return response, "\n".join(log_lines)

    except Exception as e:
        import traceback

        traceback.print_exc()
        log_lines.append(
            f"Local model execution failed: {e}. Falling back to serverless API..."
        )

    # Fallback to serverless API if local run fails
    log_lines.append(
        f"Initiating Hugging Face Serverless Inference API ({MODEL_ID})..."
    )
    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(MODEL_ID, token=os.environ.get("HF_TOKEN"))
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat_completion(messages=messages, max_tokens=512)
        response = completion.choices[0].message.content or ""
        log_lines.append("Serverless API execution completed successfully.")
        return response, "\n".join(log_lines)

    except Exception as e:
        log_lines.append(f"Serverless API execution failed: {e}.")
        log_lines.append("Falling back to local CPU heuristics...")
        return "", "\n".join(log_lines)
