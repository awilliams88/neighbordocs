from __future__ import annotations

import os
import torch
import modal
from datasets import Dataset
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
)
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer

# Define the Modal App
app = modal.App("inner-space-tuner")

# Define the container image with necessary libraries for QLoRA fine-tuning
image = modal.Image.debian_slim().pip_install(
    "torch",
    "transformers>=4.45.0",
    "peft",
    "trl",
    "accelerate",
    "bitsandbytes",
    "datasets",
    "huggingface_hub",
)

# Modal Volume to persist checkpoints and training outputs
volume = modal.Volume.from_name("inner-space-checkpoints", create_if_missing=True)

MODEL_ID = "openbmb/MiniCPM5-1B-SFT"


# Targets single A10G GPU for cost-effective execution
# Two hours timeout
@app.function(
    image=image,
    gpu="A10G",
    timeout=7200,
    volumes={"/checkpoints": volume},
)
def train_lora(hf_token: str | None = None, repo_id: str | None = None):
    """Fine-tunes openbmb/MiniCPM5-1B-SFT on cognitive behavioral reflections using QLoRA."""
    print(f"Loading tokenizer for {MODEL_ID}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
    tokenizer.pad_token = tokenizer.eos_token

    # Prepare a synthetic CBT/Mindfulness journal dataset
    print("Preparing training dataset...")
    raw_data = [
        {
            "prompt": "Today was a disaster. I made a typo in the main deployment script and broke the production build for 15 minutes. My manager was disappointed. I always screw up important things. I'm sure they are going to fire me next week.",
            "response": "=== EMOTIONS ===\n- Anxiety\n- Shame\n- Guilt\n\n=== LIFE AREAS ===\n- Career\n- Finances\n\n=== COGNITIVE DISTORTIONS ===\n- Catastrophizing (jumping to the worst outcome of being fired)\n- All-or-Nothing Thinking ('I always screw up')\n\n=== REFLECTION ===\nMaking a mistake at work is stressful, but does a single 15-minute outage define your entire capability as a developer?",
        },
        {
            "prompt": "I should have gone to the gym today. I'm so lazy. I spent the whole evening watching TV instead. I am never going to get in shape.",
            "response": "=== EMOTIONS ===\n- Guilt\n- Frustration\n- Disappointment\n\n=== LIFE AREAS ===\n- Health & Wellness\n\n=== COGNITIVE DISTORTIONS ===\n- Should Statements ('I should have gone to the gym')\n- Labeling ('I'm so lazy')\n- Overgeneralization ('I am never going to get in shape')\n\n=== REFLECTION ===\nIs there a middle ground between going to the gym and being 'lazy'? How can you show yourself compassion on rest days?",
        },
        {
            "prompt": "My partner didn't reply to my text message for five hours. They must be getting tired of me or planning to break up. I must have said something wrong.",
            "response": "=== EMOTIONS ===\n- Anxiety\n- Insecurity\n- Fear of rejection\n\n=== LIFE AREAS ===\n- Relationships\n\n=== COGNITIVE DISTORTIONS ===\n- Mind Reading (assuming they are tired of you)\n- Personalization ('I must have said something wrong')\n- Catastrophizing (jumping to a breakup)\n\n=== REFLECTION ===\nWhat are some alternative reasons your partner might not have replied, unrelated to your relationship?",
        },
        {
            "prompt": "I've been working 12-hour days all week. I feel completely exhausted, but if I take a break, my team will fall behind and it'll be my fault. I just need to push through, but I can barely think straight.",
            "response": "=== EMOTIONS ===\n- Exhaustion\n- Guilt\n- Anxiety\n\n=== LIFE AREAS ===\n- Career\n- Health & Wellness\n\n=== COGNITIVE DISTORTIONS ===\n- Should Statements ('I just need to push through')\n- Personalization (assuming sole responsibility for the team)\n- All-or-Nothing Thinking\n\n=== REFLECTION ===\nYou've been carrying a massive load. Is it truly your sole responsibility to keep the entire team afloat, or is it okay to express your limits and rest?",
        },
        {
            "prompt": "I got promoted to senior engineer, but I'm terrified. I only got it because they like me, not because I'm actually good at this. Soon they'll assign me a complex task, I'll fail, and everyone will realize I'm a fraud.",
            "response": "=== EMOTIONS ===\n- Fear\n- Insecurity\n- Imposter Syndrome\n\n=== LIFE AREAS ===\n- Career\n\n=== COGNITIVE DISTORTIONS ===\n- Discounting the Positive (overlooking the achievements that earned the promotion)\n- Mind Reading (assuming others will think you are a fraud)\n- Catastrophizing (jumping to failing and being exposed)\n\n=== REFLECTION ===\nCongratulations on your promotion! When you think they only promoted you because they 'like' you, what hard evidence of your skills and contributions are you overlooking?",
        },
        {
            "prompt": "My best friend forgot my birthday. They didn't even text me. I thought we were close, but clearly they don't value our friendship as much as I do. I should just stop talking to them entirely.",
            "response": "=== EMOTIONS ===\n- Hurt\n- Disappointment\n- Anger\n\n=== LIFE AREAS ===\n- Relationships\n\n=== COGNITIVE DISTORTIONS ===\n- All-or-Nothing Thinking ('stop talking to them entirely')\n- Mind Reading (assuming they don't value the friendship)\n- Overgeneralization\n\n=== REFLECTION ===\nIt is completely valid to feel hurt when a close friend forgets your birthday. Before deciding to end the friendship, could there be other factors in their life right now that caused them to forget?",
        },
        {
            "prompt": "I've had a headache for two days. I googled it and it says it could be a brain tumor. I'm terrified. I can't focus on anything else and I feel like my life is ending.",
            "response": "=== EMOTIONS ===\n- Panic\n- Terror\n- Health Anxiety\n\n=== LIFE AREAS ===\n- Health & Wellness\n\n=== COGNITIVE DISTORTIONS ===\n- Catastrophizing (jumping to a brain tumor)\n- Fortune Telling (believing your life is ending)\n\n=== REFLECTION ===\nHaving a persistent headache is uncomfortable and scary, but Google searches often present worst-case scenarios. Have you had similar physical symptoms in the past that turned out to be benign, like stress or dehydration?",
        },
        {
            "prompt": "I got a B on my mid-term exam. This is awful. I wanted to go to a top graduate program. Now my GPA is ruined, and I'll never get in anywhere. I'm a failure.",
            "response": "=== EMOTIONS ===\n- Despair\n- Self-Doubt\n- Fear of failure\n\n=== LIFE AREAS ===\n- Career\n- Personal Growth\n\n=== COGNITIVE DISTORTIONS ===\n- All-or-Nothing Thinking ('GPAs is ruined, never get in anywhere')\n- Labeling ('I'm a failure')\n- Catastrophizing\n\n=== REFLECTION ===\nGetting a B on a mid-term can feel disappointing when you have high standards, but does this single grade truly close all doors to your future goals?",
        },
        {
            "prompt": "I went to a networking event tonight. I tried to talk to some people, but I stuttered and made an awkward joke. Everyone probably thought I was weird and wanted me to leave. I'm never going to these events again.",
            "response": "=== EMOTIONS ===\n- Embarrassment\n- Social Anxiety\n- Loneliness\n\n=== LIFE AREAS ===\n- Relationships\n- Personal Growth\n\n=== COGNITIVE DISTORTIONS ===\n- Mind Reading (assuming everyone thought you were weird)\n- Overgeneralization ('never going to these events again')\n- Personalization\n\n=== REFLECTION ===\nSocializing can feel vulnerable. While you felt awkward, did you notice any signs that people were actually judging you, or could they have been focused on their own social anxieties?",
        },
    ]

    # Format entries using the model's chat template
    formatted_dataset = []
    for item in raw_data:
        messages = [
            {
                "role": "user",
                "content": f"You are a gentle and insightful cognitive reflection coach. Analyze the following private journal entry and provide structured feedback. Your response must contain four sections separated by '=== SECTION ===' markers:\n\n=== EMOTIONS ===\n- [Identify 1-3 dominant emotions found in the text]\n\n=== LIFE AREAS ===\n- [List 1-2 affected life areas, e.g. Work, Relationships, Health]\n\n=== COGNITIVE DISTORTIONS ===\n- [List any distortions such as Catastrophizing, All-or-Nothing thinking, or write 'None detected' if none found]\n\n=== REFLECTION ===\n[Provide a gentle, open-ended question to help the writer reflect deeper on their thoughts.]\n\nJournal entry:\n\"{item['prompt']}\"",
            },
            {"role": "assistant", "content": item["response"]},
        ]
        text = tokenizer.apply_chat_template(messages, tokenize=False)
        formatted_dataset.append({"text": text})

    dataset = Dataset.from_list(formatted_dataset)

    # Configure 4-bit QLoRA quantization for resource efficiency
    print("Configuring QLoRA...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
    )

    print(f"Loading quantized base model {MODEL_ID}...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        quantization_config=bnb_config,
        device_map="auto",
        torch_dtype=torch.bfloat16,
    )

    # Prepare model for PEFT training
    model = prepare_model_for_kbit_training(model)

    # Configure LoRA Adapter
    peft_config = LoraConfig(
        r=8,
        lora_alpha=16,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    # Configure Training Arguments
    training_args = TrainingArguments(
        output_dir="/checkpoints/inner-space-lora",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        warmup_steps=10,
        max_steps=50,
        learning_rate=2e-4,
        fp16=False,
        bf16=True,
        logging_steps=5,
        save_strategy="steps",
        save_steps=20,
        save_total_limit=2,
        report_to="none",
    )

    # Start Training
    print("Starting fine-tuning job on Modal...")
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=512,
        args=training_args,
    )
    trainer.train()
    print("Fine-tuning completed successfully!")

    # Save and push adapter to Hugging Face Hub
    print("Saving fine-tuned adapter...")
    model.save_pretrained("/checkpoints/inner-space-final")
    tokenizer.save_pretrained("/checkpoints/inner-space-final")

    # Resolve HF Token and Target Repo ID
    if not hf_token:
        hf_token = os.environ.get("HF_TOKEN")
    if not repo_id:
        repo_id = "build-small-hackathon/inner-space-1b-sft-cbt"

    # If HF token is available, push to hub
    if hf_token:
        print(
            f"Pushing fine-tuned adapter to Hugging Face Hub repository: {repo_id}..."
        )
        model.push_to_hub(repo_id, token=hf_token)
        tokenizer.push_to_hub(repo_id, token=hf_token)
        print("Pushed successfully!")
    else:
        print("HF_TOKEN not set or provided. Skipping publishing step.")
