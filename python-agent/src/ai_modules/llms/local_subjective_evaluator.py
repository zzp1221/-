"""Local Qwen3-0.6B-GGUF judge for subjective evaluation.
Mimics the exact interface and error handling of OpenAICompatibleSubjectiveJudgeEvaluator
(judge_subjective_evaluator.py:114-168) so it can be injected via the factory.
"""
from __future__ import annotations

import asyncio, json, logging, re
from typing import Any
from pathlib import Path

from pydantic import ValidationError

from src.ai_modules.models import SubjectiveJudgeEvaluation

LOGGER = logging.getLogger(__name__)


class LocalSubjectiveJudgeEvaluator:
    """CPU-based subjective judge backed by a fine-tuned Qwen3-0.6B GGUF.

    Implements the same evaluate(question, learner_answer) -> SubjectiveJudgeEvaluation
    contract as the remote evaluator, including max_retries, proper exception types,
    and score clamping to [0, 20].
    """

    SYSTEM_PROMPT = (
        "你是教育系统中的判题器，负责根据标准答案和评分要求评估主观题。"
        "请只返回 JSON 对象，字段必须为：score, isCorrect, reason, feedback, confidenceLevel。"
        "score 范围 0-20，confidenceLevel 只能是 LOW 或 MEDIUM。"
    )

    _DEFAULT_MODEL = str(
        (Path(__file__).parent.parent.parent.parent / "grpo_output" / "judge_model.gguf").resolve()
    )  # Local path; set model_path="/app/models/judge_model.gguf" for Docker

    def __init__(
        self,
        model_path: str | None = None,
        max_retries: int = 2,
        backoff_seconds: float = 0.5,
        n_ctx: int = 1024,
        n_threads: int = 4,
    ) -> None:
        from llama_cpp import Llama
        self.model = Llama(
            model_path=model_path or self._DEFAULT_MODEL,
            n_ctx=n_ctx,
            n_threads=n_threads,
            verbose=False,
        )
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    async def evaluate(
        self, *, question, learner_answer: str  # question: PracticeQuestion
    ) -> SubjectiveJudgeEvaluation:
        user_prompt = "\n".join([
            f"题目: {question.stem}",
            f"标准答案: {question.answer}",
            f"知识点: {', '.join(question.knowledge_tags) or '暂无'}",
            f"参考说明: {question.explanation}",
            f"学生答案: {learner_answer or '未作答'}",
        ])
        prompt = (
            f"<|im_start|>system\n{self.SYSTEM_PROMPT}<|im_end|>\n"
            f"<|im_start|>user\n{user_prompt}<|im_end|>\n"
            f"<|im_start|>assistant\n"
        )

        last_error: Exception | None = None
        for attempt in range(self.max_retries + 1):
            try:
                output = await asyncio.to_thread(
                    self.model, prompt, max_tokens=200, temperature=0, top_p=0.1,
                )
                text = output["choices"][0]["text"]
                data = self._extract_json(text)
                evaluation = SubjectiveJudgeEvaluation.model_validate(data)
                evaluation.score = max(0.0, min(float(evaluation.score), 20.0))
                return evaluation
            except (ValidationError, ValueError, RuntimeError, KeyError, TypeError) as exc:
                last_error = exc
                LOGGER.warning(
                    "local subjective judging attempt %s failed: %s", attempt + 1, exc
                )
                if attempt >= self.max_retries:
                    break
                await asyncio.sleep(self.backoff_seconds * (2 ** attempt))

        raise RuntimeError(f"local subjective judging failed: {last_error}")

    def _extract_json(self, text: str) -> dict[str, Any]:
        fenced = re.search(r"```json\s*(\{[\s\S]*\})\s*```", text)
        raw = fenced.group(1) if fenced else text.strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError(f"no JSON object found in model output")
        return json.loads(raw[start:end + 1])
