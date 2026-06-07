from __future__ import annotations

import os
import modal

from typing import Any

modal_any: Any = modal

# Modal app groups the remote fine-tuning job.
app = modal_any.App("inner-space-tuner")

# Container dependencies live in Modal, not the local dev environment.
image = modal_any.Image.debian_slim().pip_install(
    "torch",
    "transformers>=4.45.0",
    "peft",
    "trl",
    "accelerate",
    "bitsandbytes",
    "datasets",
    "huggingface_hub",
)

# Volume keeps checkpoints available across Modal runs.
volume = modal_any.Volume.from_name("inner-space-checkpoints", create_if_missing=True)

# Base model stays under the hackathon parameter limit.
MODEL_ID = "openbmb/MiniCPM5-1B-SFT"
ADAPTER_REPO_ID = "build-small-hackathon/inner-space-1b-sft-cbt"


@app.function(
    image=image,
    gpu="A10G",
    timeout=7200,
    volumes={"/checkpoints": volume},
    secrets=[modal_any.Secret.from_name("huggingface-secret")],
)
def train_lora(
    model_card_content: str,
    hf_token: str | None = None,
    repo_id: str | None = None,
):
    """Fine-tunes MiniCPM on six-section CBT reflections using QLoRA."""
    # Remote-only imports are installed inside the Modal container.
    import torch
    from datasets import Dataset
    from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
    )
    from trl import SFTConfig, SFTTrainer
    import io
    from huggingface_hub import login, upload_file

    # Import dataset and prompt structure from local modular file.
    from dataset import (
        build_training_prompt,
        get_training_examples,
        get_chat_training_examples,
    )

    # Tokenizer is loaded before formatting chat examples.
    print(f"Loading tokenizer for {MODEL_ID}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token

    # Synthetic examples capture reports and follow-up coaching turns.
    print("Preparing training dataset...")
    raw_data = get_training_examples()
    chat_data = get_chat_training_examples()

    # Convert report prompt/response pairs into the model chat template.
    formatted_dataset = []
    for item in raw_data:
        messages = [
            {
                "role": "user",
                "content": build_training_prompt(
                    str(item["prompt"]), int(item["distress_level"])
                ),
            },
            {"role": "assistant", "content": item["response"]},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        formatted_dataset.append({"text": text})

    # Add multi-turn examples so follow-up coaching does not drift.
    for messages in chat_data:
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        formatted_dataset.append({"text": text})

    print(f"Prepared {len(formatted_dataset)} total training conversations.")

    dataset = Dataset.from_list(formatted_dataset)

    # QLoRA keeps training feasible on a single A10G.
    print("Configuring QLoRA...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    # Load the base model in 4-bit mode for adapter training.
    print(f"Loading quantized base model {MODEL_ID}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        dtype=torch.bfloat16,
    )

    # Prepare quantized layers for PEFT adapter updates.
    model = prepare_model_for_kbit_training(model)

    # Target attention projections with enough capacity for structured reflections.
    peft_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Train long enough to learn report structure and follow-up chat behavior.
    training_args = SFTConfig(
        output_dir="/checkpoints/inner-space-lora",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=220,
        learning_rate=2e-4,
        fp16=False,
        bf16=True,
        logging_steps=5,
        save_strategy="steps",
        save_steps=55,
        save_total_limit=2,
        report_to="none",
        dataset_text_field="text",
        max_length=1536,
    )

    # Train only the adapter weights.
    print("Starting fine-tuning job on Modal...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
    )
    trainer.train()
    print("Fine-tuning completed successfully!")

    # Save the final adapter into the mounted checkpoint volume.
    print("Saving fine-tuned adapter...")
    model.save_pretrained("/checkpoints/inner-space-final")
    tokenizer.save_pretrained("/checkpoints/inner-space-final")

    # Commit the changes to the persistent volume in Modal
    print("Committing checkpoint changes to Modal Volume...")
    volume.commit()

    # Prefer explicit token and repo values when provided.
    if not hf_token:
        hf_token = os.environ.get("HF_TOKEN")
    if not repo_id:
        repo_id = ADAPTER_REPO_ID

    # Publish the adapter when Hub credentials are available.
    if hf_token:
        login(token=hf_token)
        print(
            f"Pushing fine-tuned adapter to Hugging Face Hub repository: {repo_id}..."
        )
        model.push_to_hub(repo_id)
        tokenizer.push_to_hub(repo_id)
        upload_file(
            path_or_fileobj=io.BytesIO(model_card_content.encode("utf-8")),
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model",
            commit_message="Update InnerSpace adapter model card",
        )
        print("Pushed successfully!")
    else:
        print("HF_TOKEN not set or provided. Skipping publishing step.")


@app.local_entrypoint()
def main():
    # Read CARD.md dynamically from the local filesystem during entrypoint execution.
    meta_path = os.path.join(os.path.dirname(__file__), "CARD.md")
    with open(meta_path, "r", encoding="utf-8") as f:
        model_card = f.read()

    # Launch the remote fine-tuning job from local CLI.
    train_lora.remote(model_card_content=model_card)
