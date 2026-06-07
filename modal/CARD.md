---
base_model: openbmb/MiniCPM5-1B-SFT
library_name: peft
pipeline_tag: text-generation
language:
- en
tags:
- peft
- lora
- qlora
- cbt
- journaling
- reflection
- mental-health
- build-small-hackathon
---

# InnerSpace CBT Reflection LoRA

InnerSpace CBT Reflection LoRA is a QLoRA adapter for `openbmb/MiniCPM5-1B-SFT`.
It is trained for the InnerSpace Hugging Face Space, a private journaling and
reflection app that turns a journal entry into a structured CBT-informed
reflection.

This adapter is not a clinical model. It does not provide diagnosis, treatment,
medical advice, crisis counseling, or a replacement for licensed care.

## Intended Use

- Structured reflective journaling
- Gentle CBT-informed self-reflection
- Identifying emotions, affected life areas, and common cognitive distortions
- Producing a balanced reframe, tiny next step, and reflective question
- Brief follow-up coaching when the user responds with self-critical thoughts

## Output Format

For journal analysis, the adapter is trained to produce exactly six sections:

```text
=== EMOTIONS ===
=== LIFE AREAS ===
=== COGNITIVE DISTORTIONS ===
=== BALANCED REFRAME ===
=== TINY NEXT STEP ===
=== REFLECTION ===
```

For follow-up chat, the adapter is trained to stay brief, avoid hidden reasoning
tags, avoid business-style skill metrics, validate the feeling, separate feeling
from evidence, and ask one grounded question.

## Training Recipe

- Base model: `openbmb/MiniCPM5-1B-SFT`
- Method: QLoRA with 4-bit NF4 quantization
- Adapter: rank 16 LoRA on attention projections
- Hardware: Modal NVIDIA A10G
- Training set: 30 structured journal examples and 15 multi-turn coach examples
- Sequence length: 1536 tokens
- App runtime: Hugging Face Space with local model execution only

## Safety Notes

The model should respond with supportive reflection, not certainty. It should not
diagnose the user, prescribe treatment, provide crisis intervention, or claim to
know whether the user's thoughts are objectively true. For immediate danger or
crisis situations, users should contact local emergency services or a crisis
hotline.

## Links

- Space: https://huggingface.co/spaces/build-small-hackathon/innerspace
- Source: https://github.com/awilliams88/innerspace
- Base model: https://huggingface.co/openbmb/MiniCPM5-1B-SFT
