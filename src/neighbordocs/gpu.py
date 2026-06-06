from __future__ import annotations

import os
from collections.abc import Callable

import torch

model_id = "openbmb/MiniCPM-1B-sft-bf16"
_tokenizer = None
_model = None


def get_model_and_tokenizer():
    global _model, _tokenizer
    if _model is None:
        import transformers.utils
        import transformers.utils.import_utils

        # Monkey patch to fix compatibility of OpenBMB custom code under transformers v5+
        transformers.utils.is_torch_fx_available = lambda: True
        transformers.utils.import_utils.is_torch_fx_available = lambda: True

        from transformers import AutoModelForCausalLM, AutoTokenizer

        print(f"Loading tokenizer for {model_id}...")
        _tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        print(f"Loading model {model_id}...")
        _model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            low_cpu_mem_usage=True,
            trust_remote_code=True,
        )
    return _model, _tokenizer


# ZeroGPU spaces decorator compatibility helper
try:
    import spaces
except ImportError:

    class _LocalSpacesFallback:
        @staticmethod
        def GPU(
            duration: int = 30,
        ) -> Callable[[Callable[..., str]], Callable[..., str]]:
            def decorator(function: Callable[..., str]) -> Callable[..., str]:
                return function

            return decorator

    spaces = _LocalSpacesFallback()


@spaces.GPU(duration=30)
def _generate_on_gpu(prompt: str) -> str:
    model, tokenizer = get_model_and_tokenizer()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Moving model to device: {device}...")
    model.to(device)

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
    generated_ids = [
        output_ids[len(input_ids) :]
        for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
    ]
    response = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    return response


def run_model_inference(prompt: str, use_zerogpu: bool = False) -> tuple[str, str]:
    """Runs model inference using local ZeroGPU or Serverless Inference API fallback.

    Returns:
        tuple[str, str]: (response_text, log_details)
    """
    log_lines = []

    if use_zerogpu:
        if torch.cuda.is_available():
            log_lines.append(
                "ZeroGPU hardware detected. Initiating local GPU execution..."
            )
            try:
                response = _generate_on_gpu(prompt)
                log_lines.append("Local GPU execution completed successfully.")
                return response, "\n".join(log_lines)
            except Exception as e:
                log_lines.append(
                    f"Local GPU execution failed: {str(e)}. Falling back to serverless API..."
                )
        else:
            log_lines.append(
                "ZeroGPU requested, but CUDA is not available. Falling back to serverless API..."
            )

    # Serverless API Fallback
    log_lines.append(
        f"Initiating Hugging Face Serverless Inference API ({model_id})..."
    )
    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(model_id, token=os.environ.get("HF_TOKEN"))
        messages = [{"role": "user", "content": prompt}]
        completion = client.chat_completion(messages=messages, max_tokens=512)
        response = completion.choices[0].message.content
        log_lines.append("Serverless API execution completed successfully.")
        return response, "\n".join(log_lines)
    except Exception as e:
        log_lines.append(f"Serverless API execution failed: {str(e)}.")
        log_lines.append("Falling back to local CPU heuristics...")
        return "", "\n".join(log_lines)
