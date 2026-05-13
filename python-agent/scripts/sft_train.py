"""
SFT Stage 1: Train Qwen3-0.6B to mimic teacher evaluator.
FP16 + LoRA (no quantization needed for 0.6B model).

Usage:
  .venv-train/Scripts/python scripts/sft_train.py           # full data
  .venv-train/Scripts/python scripts/sft_train.py --N 500   # 500 samples
  .venv-train/Scripts/python scripts/sft_train.py --dryrun  # 1 batch test
"""
from __future__ import annotations

import json, os, sys

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    TrainingArguments,
)

# ── Config ──────────────────────────────────────────────────
MODEL_NAME = "Qwen/Qwen3-0.6B"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "sft_output")
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "judge_train_data.json")
EPOCHS = 2
LEARNING_RATE = 2e-4
LORA_R = 8
LORA_ALPHA = 16
BATCH_SIZE = 2
GRAD_ACCUM = 8                 # effective batch = 16
MAX_SEQ_LENGTH = 1024

SYSTEM_PROMPT = (
    "你是教育系统中的判题器，负责根据标准答案和评分要求评估主观题。"
    "请只返回 JSON 对象，字段必须为：score, isCorrect, reason, feedback, confidenceLevel。"
    "score 范围 0-20，confidenceLevel 只能是 LOW 或 MEDIUM。"
)


def format_sample(sample: dict) -> str:
    user = "\n".join([
        f"题目: {sample['stem']}",
        f"标准答案: {sample['answer']}",
        f"知识点: {', '.join(sample.get('knowledge_tags', [])) or '暂无'}",
        f"参考说明: {sample.get('explanation', '')}",
        f"学生答案: {sample['learner_answer'] or '未作答'}",
    ])
    return (
        f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
        f"<|im_start|>user\n{user}<|im_end|>\n"
        f"<|im_start|>assistant\n"
        f"{json.dumps(sample['label'], ensure_ascii=False)}"
        f"<|im_end|>"
    )


def load_data(max_samples: int | None = None) -> Dataset:
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)
    if max_samples and max_samples < len(raw):
        raw = raw[:max_samples]
    texts = [format_sample(s) for s in raw]
    print(f"  Loaded {len(raw)} samples")
    return Dataset.from_dict({"text": texts})


def main():
    limit = None
    dryrun = "--dryrun" in sys.argv
    for i, arg in enumerate(sys.argv):
        if arg == "--N" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])

    print("=" * 60)
    print(f"SFT Training: {MODEL_NAME} (FP16 + LoRA)")
    print(f"Data: {DATA_FILE}" + (f" -> {limit} samples" if limit else ""))
    print("=" * 60)

    # 1. Load model in FP16
    print("\n[1/4] Loading model (FP16)...")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    lora_config = LoraConfig(
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 2. Data
    print("\n[2/4] Preparing training data...")
    dataset = load_data(limit)
    if dryrun:
        dataset = dataset.select(range(min(2, len(dataset))))
        print("  DRY RUN: 2 samples")

    def tokenize(examples):
        tokenized = tokenizer(examples["text"], truncation=True,
                              padding="max_length", max_length=MAX_SEQ_LENGTH)
        tokenized["labels"] = tokenized["input_ids"].copy()
        return tokenized
    dataset = dataset.map(tokenize, batched=True)

    # 3. Train
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"\n[3/4] Training on {gpu} ({EPOCHS} epochs, lr={LEARNING_RATE})...")

    from transformers import Trainer
    trainer = Trainer(
        model=model,
        args=TrainingArguments(
            output_dir=OUTPUT_DIR,
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM,
            num_train_epochs=EPOCHS,
            learning_rate=LEARNING_RATE,
            fp16=True,
            logging_steps=20,
            save_steps=200,
            save_total_limit=2,
            optim="adamw_torch",
            report_to="none",
        ),
        train_dataset=dataset,
    )
    trainer.train()

    # 4. Save
    print(f"\n[4/4] Saving to {OUTPUT_DIR}...")
    merged = model.merge_and_unload()
    merged.save_pretrained(os.path.join(OUTPUT_DIR, "merged"), safe_serialization=True)
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "merged"))

    print("\nDone!")
    print(f"  Model: {OUTPUT_DIR}/merged/")
    print(f"Next: Convert to GGUF, then GRPO training")


if __name__ == "__main__":
    main()
