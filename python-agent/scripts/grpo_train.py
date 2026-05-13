"""
GRPO Stage 2: Refine judge model using group-relative reward.
Each training sample: 3 answers to the same question form a comparison group.
Reward = keyword_coverage*0.5 + structure*0.5

Usage:
  .venv-train/Scripts/python scripts/grpo_train.py
  .venv-train/Scripts/python scripts/grpo_train.py --N 200
  .venv-train/Scripts/python scripts/grpo_train.py --dryrun
"""
from __future__ import annotations

import json, os, sys, random, re
from collections import defaultdict
from pathlib import Path

# Fix trl on Windows: force UTF-8 for reading jinja templates
_orig_read = Path.read_text
def _patched_read(self, encoding="utf-8", errors=None):
    return _orig_read(self, encoding=encoding, errors=errors)
Path.read_text = _patched_read

import torch
from datasets import Dataset
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOConfig, GRPOTrainer

# ── Config ──
SFT_MODEL = os.path.join(os.path.dirname(__file__), "..", "sft_output", "merged")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "grpo_output")
DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "judge_train_data.json")
EPOCHS = 2
LEARNING_RATE = 5e-5
LORA_R = 8
LORA_ALPHA = 16
BATCH_SIZE = 4
GRAD_ACCUM = 2
MAX_PROMPT_LENGTH = 800
MAX_COMPLETION_LENGTH = 256
NUM_GENERATIONS = 4

SYSTEM_PROMPT = (
    "你是教育系统中的判题器，负责根据标准答案和评分要求评估主观题。"
    "请只返回 JSON 对象，字段必须为：score, isCorrect, reason, feedback, confidenceLevel。"
    "score 范围 0-20，confidenceLevel 只能是 LOW 或 MEDIUM。"
)

# ── Reward functions ──

def _normalize(text: str) -> str:
    return re.sub(r"[\s_\-]+", "", str(text).strip().upper())


def keyword_coverage(label: dict, reference_answer: str) -> float:
    """How well does the judged score align with keyword overlap?"""
    keywords = [kw for kw in re.split(r"[，。、；：\s]+", reference_answer) if len(kw) >= 2]
    if not keywords:
        return 0.5
    matched = sum(1 for kw in keywords if _normalize(kw) in _normalize(json.dumps(label, ensure_ascii=False)))
    return min(1.0, matched / max(len(keywords), 1))


def structure_score(label_str: str) -> float:
    """Does the output contain valid JSON with required fields?"""
    required = ["score", "isCorrect", "reason", "feedback", "confidenceLevel"]
    try:
        data = json.loads(label_str)
        present = sum(1 for f in required if f in data)
        is_valid = (
            isinstance(data.get("score"), (int, float))
            and isinstance(data.get("isCorrect"), bool)
            and data.get("confidenceLevel") in ("LOW", "MEDIUM")
        )
        return (present / len(required)) * 0.5 + (0.5 if is_valid else 0.0)
    except (json.JSONDecodeError, TypeError):
        return 0.0


def compute_reward(completions: list[str], prompts: list[str] | None = None, **kwargs) -> list[float]:
    """Group-relative reward: correct > wrong in the same group."""
    rewards = []
    for completion in completions:
        try:
            match = re.search(r"\{[\s\S]*\}", completion)
            label_str = match.group() if match else completion
        except Exception:
            label_str = completion

        # Extract reference answer from the prompt if available
        ref = ""
        if prompts and len(prompts) > 0:
            ref_match = re.search(r"标准答案:\s*(.+?)\n", prompts[min(len(rewards), len(prompts)-1)])
            ref = ref_match.group(1) if ref_match else ""

        kw = keyword_coverage({"raw": label_str}, ref) if ref else 0.5
        st = structure_score(label_str)
        rewards.append(kw * 0.5 + st * 0.5)
    return rewards


# ── Data preparation ──

def prepare_grpo_data(max_samples: int | None = None) -> Dataset:
    """Group samples by (stem, answer) to form comparison groups for GRPO."""
    with open(DATA_FILE, encoding="utf-8") as f:
        raw = json.load(f)

    # Group by stem+answer (same question, different learner answers)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for s in raw:
        key = (s["stem"], s["answer"])
        groups[key].append(s)

    # Keep only groups with all 3 variants
    complete_groups = {k: v for k, v in groups.items() if len(v) == 3}

    items = list(complete_groups.values())
    if max_samples and max_samples < len(items):
        random.shuffle(items)
        items = items[:max_samples]

    prompts = []
    for group in items:
        for sample in group:
            prompt = (
                f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n"
                f"<|im_start|>user\n"
                f"题目: {sample['stem']}\n"
                f"标准答案: {sample['answer']}\n"
                f"知识点: {', '.join(sample.get('knowledge_tags', [])) or '暂无'}\n"
                f"参考说明: {sample.get('explanation', '')}\n"
                f"学生答案: {sample['learner_answer'] or '未作答'}\n"
                f"<|im_end|>\n"
                f"<|im_start|>assistant\n"
            )
            prompts.append(prompt)

    print(f"  Groups: {len(items)} | Samples: {len(prompts)}")
    return Dataset.from_dict({"prompt": prompts})


def main():
    limit = None
    dryrun = "--dryrun" in sys.argv
    resume = "--resume" in sys.argv
    seed_val = 42
    for i, arg in enumerate(sys.argv):
        if arg == "--N" and i + 1 < len(sys.argv):
            limit = int(sys.argv[i + 1])
        if arg == "--seed" and i + 1 < len(sys.argv):
            seed_val = int(sys.argv[i + 1])
    random.seed(seed_val)

    print("=" * 60)
    print("GRPO Training (Group Relative Policy Optimization)")
    print(f"SFT base: {SFT_MODEL}")
    print(f"Data: {DATA_FILE}" + (f" -> {limit} groups" if limit else ""))
    print("=" * 60)

    # 1. Load SFT model
    print("\n[1/4] Loading SFT model...")
    model = AutoModelForCausalLM.from_pretrained(
        SFT_MODEL, dtype=torch.float16, device_map="auto", trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(SFT_MODEL, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    lora_config = LoraConfig(
        r=LORA_R, lora_alpha=LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                        "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05, bias="none", task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora_config)

    # 2. Data
    print("\n[2/4] Preparing GRPO data...")
    dataset = prepare_grpo_data(limit)
    if dryrun:
        dataset = dataset.select(range(min(6, len(dataset))))
        print("  DRY RUN")

    # 3. Train
    gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
    print(f"\n[3/4] GRPO Training on {gpu} ({EPOCHS} epochs)...")

    trainer = GRPOTrainer(
        model=model,
        reward_funcs=compute_reward,
        args=GRPOConfig(
            output_dir=OUTPUT_DIR,
            per_device_train_batch_size=BATCH_SIZE,
            gradient_accumulation_steps=GRAD_ACCUM,
            num_train_epochs=EPOCHS,
            learning_rate=LEARNING_RATE,
            fp16=True,
            logging_steps=10,
            save_steps=100,
            save_total_limit=2,
            optim="adamw_torch",
            report_to="none",
            max_grad_norm=1.0,
        ),
        train_dataset=dataset,
        processing_class=tokenizer,
    )
    ckpt = None
    if resume:
        ckpt_dirs = sorted(Path(OUTPUT_DIR).glob("checkpoint-*"))
        if ckpt_dirs:
            ckpt = str(ckpt_dirs[-1])
            print(f"\nResuming from: {ckpt}")
        else:
            print("\nNo checkpoint found, training from scratch")

    trainer.train(resume_from_checkpoint=ckpt)

    # 4. Save
    print(f"\n[4/4] Saving to {OUTPUT_DIR}...")
    model = model.merge_and_unload()
    model.save_pretrained(os.path.join(OUTPUT_DIR, "merged"), safe_serialization=True)
    tokenizer.save_pretrained(os.path.join(OUTPUT_DIR, "merged"))

    print(f"\nDone!")
    print(f"  GRPO Model: {OUTPUT_DIR}/merged/")
    print(f"Next: Convert to GGUF for deployment")


if __name__ == "__main__":
    main()
