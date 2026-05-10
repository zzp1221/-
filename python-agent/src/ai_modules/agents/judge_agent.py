"""Judge agent backed by AgentCoreLoop and structured scoring output."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.async_utils import cancel_and_await
from src.ai_modules.llms import (
    HeuristicSubjectiveJudgeEvaluator,
    JudgeLLMClientFactory,
    JudgeFeedbackGenerator,
    ObjectiveJudgeGenerator,
    SubjectiveJudgeEvaluatorFactory,
)
from src.ai_modules.memory import InMemoryPracticeStore, PostgresPracticeStore, PracticeStore
from src.ai_modules.models import (
    JudgeItemResult,
    JudgeResultPayload,
    JudgeResultSSEEvent,
    PracticeQuestion,
    ProgressPayload,
    ProgressSSEEvent,
    SSEEvent,
    SubjectiveJudgeEvaluation,
)
from src.ai_modules.prompts import build_judge_system_prompt
from src.ai_modules.runtime import (
    AgentCoreLoop,
    PermissionLevel,
    RecoveryEngine,
    SystemSnapshot,
    ToolRegistry,
)


class JudgeAgent(PlaceholderAgent):
    """Grade learner answers and summarize profile-impacting deltas."""

    def __init__(
        self,
        llm_client: Any | None = None,
        practice_store: PracticeStore | None = None,
        subjective_evaluator: Any | None = None,
        objective_judge_generator: Any | None = None,
        feedback_generator: Any | None = None,
        heartbeat_interval_seconds: float = 15.0,
    ) -> None:
        super().__init__("Judge Agent", "judge")
        self.llm_client = llm_client or JudgeLLMClientFactory.create()
        self.practice_store = practice_store or PostgresPracticeStore()
        self.fallback_practice_store = InMemoryPracticeStore()
        self.subjective_evaluator = subjective_evaluator or SubjectiveJudgeEvaluatorFactory.create()
        self.fallback_subjective_evaluator = HeuristicSubjectiveJudgeEvaluator()
        self.objective_judge_generator = objective_judge_generator or ObjectiveJudgeGenerator()
        self.feedback_generator = feedback_generator or JudgeFeedbackGenerator()
        self.heartbeat_interval_seconds = heartbeat_interval_seconds

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_judge_system_prompt(snapshot)

    async def run(
        self,
        *,
        task_id: str,
        trace_id: str,
        seq: int,
        service_type: str,
        params: dict,
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> AsyncIterator[SSEEvent]:
        del service_type, snapshot
        user_id = str(params.get("userId") or "00000000-0000-0000-0000-000000000001")
        next_seq = seq
        judge_result: dict[str, Any] | None = None
        judge_result_task = asyncio.create_task(
            self._run_agent_core_loop(
                task_id=task_id,
                user_id=user_id,
                params=params,
                system_prompt=system_prompt,
            )
        )
        try:
            while not judge_result_task.done():
                try:
                    judge_result = await asyncio.wait_for(
                        asyncio.shield(judge_result_task),
                        timeout=self.heartbeat_interval_seconds,
                    )
                    break
                except TimeoutError:
                    yield ProgressSSEEvent(
                        taskId=task_id,
                        traceId=trace_id,
                        seq=next_seq,
                        payload=ProgressPayload(
                            stage=self.stage_name,
                            percent=70,
                            message="判题仍在执行中，请稍候",
                        ),
                    )
                    next_seq += 1
            else:
                judge_result = await judge_result_task
        except asyncio.CancelledError:
            await cancel_and_await(judge_result_task)
            raise

        if judge_result is None:
            judge_result = await judge_result_task
        params["judgeResult"] = judge_result
        params["profileSource"] = "PRACTICE"

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=80,
                message="已完成判题并生成反馈",
            ),
        )
        yield JudgeResultSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq + 1,
            payload=JudgeResultPayload.model_validate(judge_result),
        )

    async def _run_agent_core_loop(
        self,
        *,
        task_id: str,
        user_id: str,
        params: dict[str, Any],
        system_prompt: str,
    ) -> dict[str, Any]:
        tool_registry = ToolRegistry()
        tool_registry.register(
            name="grade_objective",
            fn=lambda tool_input: self._tool_grade_objective(tool_input=tool_input, params=params),
            permission_level=PermissionLevel.SYSTEM_WRITE,
            description="Grade objective questions. Returns dict with 'items' and 'pendingSubjective'.",
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )
        tool_registry.register(
            name="evaluate_subjective",
            fn=lambda tool_input: self._tool_evaluate_subjective(tool_input=tool_input, params=params),
            permission_level=PermissionLevel.SYSTEM_WRITE,
            description="Evaluate subjective questions. Pass the output of grade_objective directly as input.",
            parameters={
                "type": "object",
                "properties": {
                    "items": {"type": "array", "description": "Graded items from grade_objective"},
                    "pendingSubjective": {"type": "array", "description": "Pending subjective questions"},
                },
                "required": ["items"],
            },
        )
        tool_registry.register(
            name="generate_feedback",
            fn=lambda tool_input: self._tool_generate_feedback(tool_input=tool_input, params=params),
            permission_level=PermissionLevel.SYSTEM_WRITE,
            description="Generate feedback summary. Pass the output of evaluate_subjective directly as input.",
            parameters={
                "type": "object",
                "properties": {
                    "items": {"type": "array", "description": "All judged items"},
                },
                "required": ["items"],
            },
        )
        tool_registry.register(
            name="save_practice_result",
            fn=lambda tool_input: self._tool_save_practice_result(
                tool_input=tool_input,
                task_id=task_id,
                user_id=user_id,
                params=params,
            ),
            permission_level=PermissionLevel.SYSTEM_WRITE,
            description="Save practice result. Pass the output of generate_feedback directly as input.",
            parameters={
                "type": "object",
                "properties": {
                    "summary": {"type": "string"},
                    "totalScore": {"type": "number"},
                    "accuracy": {"type": "number"},
                    "items": {"type": "array"},
                    "weakKnowledgeTags": {"type": "array"},
                },
                "required": ["items"],
            },
        )
        result = await AgentCoreLoop(
            llm_client=self.llm_client,
            tool_registry=tool_registry,
            recovery_engine=RecoveryEngine(),
            max_iterations=7,
            agent_level=PermissionLevel.SYSTEM_WRITE,
        ).run(
            system_prompt=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": f"请对练习结果进行判题并生成反馈，任务 {task_id}。",
                }
            ],
        )
        output = result.tool_results[-1].output if result.tool_results else {}
        return output if isinstance(output, dict) else {}

    async def _tool_grade_objective(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        try:
            return await self.objective_judge_generator.judge(
                questions=self._questions(params),
                answers=self._answers(params),
            )
        except Exception:
            objective_results: list[dict[str, Any]] = []
            subjective_questions: list[dict[str, Any]] = []
            for question in self._questions(params):
                answer = self._answers(params).get(question.question_id, "")
                if question.question_type == "SHORT_ANSWER":
                    subjective_questions.append(question.model_dump(by_alias=True))
                    continue
                is_correct = self._normalize_text(answer) == self._normalize_text(question.answer)
                objective_results.append(
                    JudgeItemResult(
                        questionId=question.question_id,
                        questionType=question.question_type,
                        learnerAnswer=answer,
                        correctAnswer=question.answer,
                        isCorrect=is_correct,
                        score=20.0 if is_correct else 0.0,
                        knowledgeTags=question.knowledge_tags,
                        reason="答案匹配标准答案" if is_correct else "答案与标准答案不一致",
                        feedback="这道客观题判断正确。" if is_correct else "先回到题目条件，确认再作答。",
                        profileDelta=self._build_profile_delta(question=question, is_correct=is_correct),
                    ).model_dump(by_alias=True)
                )
            return {"items": objective_results, "pendingSubjective": subjective_questions}

    async def _tool_evaluate_subjective(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        judged_items = list(tool_input.get("items", []))
        for question_payload in tool_input.get("pendingSubjective", []):
            question = PracticeQuestion.model_validate(question_payload)
            learner_answer = self._answers(params).get(question.question_id, "")
            evaluation = await self._safe_evaluate_subjective(
                question=question,
                learner_answer=learner_answer,
            )
            judged_items.append(
                JudgeItemResult(
                    questionId=question.question_id,
                    questionType=question.question_type,
                    learnerAnswer=learner_answer,
                    correctAnswer=question.answer,
                    isCorrect=evaluation.is_correct,
                    score=evaluation.score,
                    knowledgeTags=question.knowledge_tags,
                    reason=evaluation.reason,
                    feedback=evaluation.feedback,
                    profileDelta=self._build_profile_delta(
                        question=question,
                        is_correct=evaluation.is_correct,
                        confidence_level=evaluation.confidence_level,
                    ),
                ).model_dump(by_alias=True)
            )
        return {"items": judged_items}

    async def _tool_generate_feedback(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        items = [JudgeItemResult.model_validate(item) for item in tool_input.get("items", [])]
        try:
            topic = (
                params.get("topic")
                or params.get("query")
                or tool_input.get("topic")
                or "当前主题"
            )
            return await self.feedback_generator.summarize(items=items, topic=str(topic))
        except Exception:
            total_score = sum(item.score for item in items)
            full_score = 20.0 * len(items) if items else 1.0
            accuracy = sum(1 for item in items if item.is_correct) / max(len(items), 1)
            incorrect_tags = [
                tag
                for item in items
                if not item.is_correct
                for tag in item.knowledge_tags
            ]
            summary = (
                f"本次共判定 {len(items)} 题，得分 {total_score:.1f} / {full_score:.1f}，"
                f"正确率 {accuracy:.0%}。"
            )
            return {
                "summary": summary,
                "totalScore": round(total_score, 2),
                "accuracy": round(accuracy, 4),
                "items": [item.model_dump(by_alias=True) for item in items],
                "weakKnowledgeTags": list(dict.fromkeys(incorrect_tags)),
            }

    async def _tool_save_practice_result(
        self,
        *,
        tool_input: dict[str, Any],
        task_id: str,
        user_id: str,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        batch = params.get("practiceQuestionBatch", {})
        topic = str(batch.get("topic") or params.get("topic") or params.get("query") or "当前主题")
        judge_payload = JudgeResultPayload(
            title=f"{topic} 判题结果",
            summary=str(tool_input.get("summary", "判题完成。")),
            totalScore=float(tool_input.get("totalScore", 0.0)),
            accuracy=float(tool_input.get("accuracy", 0.0)),
            items=[
                JudgeItemResult.model_validate(item)
                for item in tool_input.get("items", [])
            ],
        )
        payload = judge_payload.model_dump(by_alias=True)
        payload["taskId"] = task_id
        payload["weakKnowledgeTags"] = list(tool_input.get("weakKnowledgeTags", []))
        persistence_metadata = await self._safe_save_judge_result(
            user_id=user_id,
            answers=self._answers(params),
            judge_result=judge_payload,
            persistence_metadata=params.get("practicePersistence"),
        )
        params["practiceJudgePersistence"] = persistence_metadata
        payload["persistence"] = persistence_metadata
        return payload

    def _questions(self, params: dict[str, Any]) -> list[PracticeQuestion]:
        raw_questions = (
            params.get("practiceQuestions")
            or params.get("practiceQuestionBatch", {}).get("questions", [])
        )
        return [PracticeQuestion.model_validate(question) for question in raw_questions]

    def _answers(self, params: dict[str, Any]) -> dict[str, str]:
        raw_answers = params.get("answers", {})
        if isinstance(raw_answers, dict):
            return {str(key): str(value) for key, value in raw_answers.items()}
        if isinstance(raw_answers, list):
            normalized: dict[str, str] = {}
            for item in raw_answers:
                if not isinstance(item, dict):
                    continue
                question_id = item.get("questionId") or item.get("id")
                if question_id is None:
                    continue
                normalized[str(question_id)] = str(item.get("answer", ""))
            return normalized
        return {}

    def _build_profile_delta(
        self,
        *,
        question: PracticeQuestion,
        is_correct: bool,
        confidence_level: str | None = None,
    ) -> dict[str, str | list[str]]:
        if is_correct:
            return {"confidenceLevel": confidence_level or "MEDIUM"}
        return {
            "confidenceLevel": confidence_level or "LOW",
            "weakPoints": question.knowledge_tags,
        }

    async def _safe_evaluate_subjective(
        self,
        *,
        question: PracticeQuestion,
        learner_answer: str,
    ) -> SubjectiveJudgeEvaluation:
        try:
            return await self.subjective_evaluator.evaluate(
                question=question,
                learner_answer=learner_answer,
            )
        except Exception:
            return await self.fallback_subjective_evaluator.evaluate(
                question=question,
                learner_answer=learner_answer,
            )

    def _normalize_text(self, value: str) -> str:
        return "".join(str(value).strip().upper().split())

    async def _safe_save_judge_result(
        self,
        *,
        user_id: str,
        answers: dict[str, str],
        judge_result: JudgeResultPayload,
        persistence_metadata: dict[str, Any] | None,
    ) -> dict[str, Any]:
        try:
            return await self.practice_store.save_judge_result(
                user_id=user_id,
                answers=answers,
                judge_result=judge_result,
                persistence_metadata=persistence_metadata,
            )
        except Exception:
            return await self.fallback_practice_store.save_judge_result(
                user_id=user_id,
                answers=answers,
                judge_result=judge_result,
                persistence_metadata=persistence_metadata,
            )
