from __future__ import annotations

import os
import re
from typing import Any
import torch
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer

from env.config import ADAPTER_REPO_ID, MODEL_ID

# Keep one model instance warm after the first request.
_model: Any = None
_tokenizer: Any = None

# Reasoning-capable models sometimes emit hidden thinking tags.
_THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.IGNORECASE | re.DOTALL)
_THINK_START_PATTERN = re.compile(r"<think>.*", re.IGNORECASE | re.DOTALL)


def clean_generated_text(text: str, max_sentences: int | None = None) -> str:
    """Removes hidden reasoning and trims rambling generated text."""
    # Prefer content after a closing reasoning tag if the model included one.
    if "</think>" in text.lower():
        text = re.split(r"</think>", text, flags=re.IGNORECASE, maxsplit=1)[-1]

    # Remove complete or dangling reasoning blocks.
    text = _THINK_BLOCK_PATTERN.sub("", text)
    text = _THINK_START_PATTERN.sub("", text)

    # Drop accidental chat-template continuations.
    for marker in ("<|im_end|>", "<|im_start|>", "\nUser:", "\nAssistant:"):
        if marker in text:
            text = text.split(marker, 1)[0]

    # Normalize horizontal whitespace, but preserve newlines.
    text = re.sub(r"[ \t]+", " ", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if max_sentences is None or not text:
        return text

    # Keep coach replies compact for the visible chat panel.
    sentences = re.findall(r"[^.!?]+[.!?]?", text)
    compact = "".join(sentences[:max_sentences]).strip()
    return compact or text


def get_model_and_tokenizer(log_lines: list[str]) -> tuple[Any, Any]:
    """Loads and caches the Hugging Face model and tokenizer lazily."""
    global _model, _tokenizer
    if _model is None:
        # Load tokenizer before model so prompt formatting is ready.
        log_lines.append(f"Loading tokenizer: {MODEL_ID}")
        _tokenizer = AutoTokenizer.from_pretrained(
            MODEL_ID,
            token=os.environ.get("HF_TOKEN"),
        )

        # Use bfloat16 on CUDA and float32 elsewhere for compatibility.
        log_lines.append(f"Loading model: {MODEL_ID}")
        dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
        _model = AutoModelForCausalLM.from_pretrained(
            MODEL_ID,
            dtype=dtype,
            low_cpu_mem_usage=True,
            token=os.environ.get("HF_TOKEN"),
        )

        # Apply the CBT adapter when it is available.
        log_lines.append(f"Loading LoRA adapter: {ADAPTER_REPO_ID}")
        try:
            _model = PeftModel.from_pretrained(
                _model,
                ADAPTER_REPO_ID,
                token=os.environ.get("HF_TOKEN"),
            )
            log_lines.append("LoRA adapter applied.")
        except Exception as adapter_error:
            log_lines.append(
                f"Warning: Could not load adapter ({adapter_error}). Using base model."
            )

        # Move the loaded model to GPU memory when ZeroGPU is active.
        if torch.cuda.is_available():
            log_lines.append("Moving model to CUDA.")
            _model = _model.to("cuda")

    return _model, _tokenizer


def run_model_inference(prompt: str) -> tuple[str, str]:
    """Executes inference using local hardware in the app runtime."""
    log_lines: list[str] = []
    try:
        # Reuse the cached local model for the journal analysis.
        log_lines.append("Initializing local model execution...")
        model, tokenizer = get_model_and_tokenizer(log_lines)
        device = str(model.device)
        log_lines.append(f"Running local model execution on device: {device}...")

        # Format the prompt with the model chat template.
        messages = [{"role": "user", "content": prompt}]
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        # Generate a structured CBT reflection.
        log_lines.append("Generating reflection...")
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
        )

        # Decode only the generated assistant tokens.
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        response = clean_generated_text(response)
        log_lines.append("Local model execution completed successfully.")
        return response, "\n".join(log_lines)

    except Exception as e:
        # Keep private text local even when inference fails.
        log_lines.append(f"Local model execution failed: {e}.")
        log_lines.append("Inference stopped. No serverless fallback is configured.")
        return "", "\n".join(log_lines)


def run_chat_inference(
    history: list[dict[str, str]],
    system_prompt: str,
) -> tuple[str, str]:
    """Executes stateful multi-turn chat generation using local hardware."""
    log_lines: list[str] = []
    try:
        # Reuse the cached local model for follow-up coaching.
        log_lines.append("Initializing local model for chat...")
        model, tokenizer = get_model_and_tokenizer(log_lines)
        device = str(model.device)
        log_lines.append(f"Running local chat model on device: {device}...")

        # Include the system prompt and visible chat history.
        messages = [{"role": "system", "content": system_prompt}] + history
        text = tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(device)

        # Keep chat replies shorter than the initial report.
        log_lines.append("Generating chat response...")
        generated_ids = model.generate(
            **model_inputs,
            max_new_tokens=128,
            do_sample=True,
            temperature=0.45,
            top_p=0.85,
            repetition_penalty=1.08,
        )

        # Decode only the latest assistant response.
        generated_ids = [
            output_ids[len(input_ids) :]
            for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
        ]
        response: str = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
        response = clean_generated_text(response, max_sentences=4)
        if not response:
            response = (
                "That sounds like a painful thought to sit with. "
                "Can we look at one concrete piece of evidence for and against it?"
            )
        log_lines.append("Local chat generation completed successfully.")
        return response, "\n".join(log_lines)

    except Exception as e:
        # Preserve privacy by failing locally instead of routing to an API.
        log_lines.append(f"Local chat execution failed: {e}.")
        log_lines.append(
            "Chat inference stopped. No serverless fallback is configured."
        )
        error_msg = (
            "I'm sorry, local model execution is currently unavailable. "
            "Please try again after the Space finishes loading the model."
        )
        return error_msg, "\n".join(log_lines)
