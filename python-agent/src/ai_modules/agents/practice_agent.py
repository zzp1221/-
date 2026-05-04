"""Practice agent backed by AgentCoreLoop and structured question batch output."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import PracticeLLMClientFactory, PracticeQuestionGenerator
from src.ai_modules.memory import InMemoryPracticeStore, PostgresPracticeStore, PracticeStore
from src.ai_modules.models import (
    ProgressPayload,
    ProgressSSEEvent,
    PracticeQuestion,
    QuestionBatchPayload,
    QuestionBatchSSEEvent,
    SSEEvent,
)
from src.ai_modules.prompts import build_practice_system_prompt
from src.ai_modules.runtime import (
    AgentCoreLoop,
    PermissionLevel,
    RecoveryEngine,
    SystemSnapshot,
    ToolRegistry,
)


class PracticeAgent(PlaceholderAgent):
    """Generate practice questions aligned with learner context."""

    def __init__(
        self,
        llm_client: Any | None = None,
        practice_store: PracticeStore | None = None,
        question_generator: Any | None = None,
        heartbeat_interval_seconds: float = 15.0,
    ) -> None:
        super().__init__("Practice Agent", "practice")
        self.llm_client = llm_client or PracticeLLMClientFactory.create()
        self.practice_store = practice_store or PostgresPracticeStore()
        self.fallback_practice_store = InMemoryPracticeStore()
        self.question_generator = question_generator or PracticeQuestionGenerator()
        self.heartbeat_interval_seconds = heartbeat_interval_seconds

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_practice_system_prompt(snapshot)

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
        question_batch_task = asyncio.create_task(
            self._run_agent_core_loop(
                params=params,
                system_prompt=system_prompt,
            )
        )
        while not question_batch_task.done():
            try:
                question_batch = await asyncio.wait_for(
                    asyncio.shield(question_batch_task),
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
                        percent=35,
                        message="练习题仍在生成中，请稍候",
                    ),
                )
                next_seq += 1
        else:
            question_batch = await question_batch_task

        question_batch = question_batch if "question_batch" in locals() else await question_batch_task
        params["practiceQuestionBatch"] = question_batch
        params["practiceQuestions"] = question_batch["questions"]
        params["practicePersistence"] = await self._safe_save_question_batch(
            user_id=user_id,
            task_id=task_id,
            question_batch=QuestionBatchPayload.model_validate(question_batch),
        )

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=55,
                message="已生成练习题批次",
            ),
        )
        yield QuestionBatchSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=next_seq + 1,
            payload=QuestionBatchPayload.model_validate(question_batch),
        )

    async def _run_agent_core_loop(
        self,
        *,
        params: dict[str, Any],
        system_prompt: str,
    ) -> dict[str, Any]:
        tool_registry = ToolRegistry()
        tool_registry.register(
            name="generate_questions",
            fn=lambda tool_input: self._tool_generate_questions(tool_input=tool_input, params=params),
            permission_level=PermissionLevel.CONTENT_GENERATE,
            description="Generate a practice question set for the current topic. Returns a dict with 'title', 'topic', 'difficulty', 'questions'.",
            parameters={
                "type": "object",
                "properties": {},
                "additionalProperties": False,
            },
        )
        tool_registry.register(
            name="validate_question",
            fn=self._tool_validate_question,
            permission_level=PermissionLevel.CONTENT_GENERATE,
            description="Validate generated practice questions. Pass the output of generate_questions directly as input.",
            parameters={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Batch title"},
                    "topic": {"type": "string", "description": "Topic name"},
                    "difficulty": {"type": "string", "description": "Difficulty level"},
                    "questions": {
                        "type": "array",
                        "description": "Questions from generate_questions",
                        "items": {"type": "object"},
                    },
                },
                "required": ["questions"],
            },
        )
        tool_registry.register(
            name="format_question_batch",
            fn=lambda tool_input: self._tool_format_question_batch(tool_input=tool_input, params=params),
            permission_level=PermissionLevel.CONTENT_GENERATE,
            description="Format the validated questions into a standard batch payload. Pass the output of validate_question directly as input.",
            parameters={
                "type": "object",
                "properties": {
                    "topic": {"type": "string"},
                    "difficulty": {"type": "string"},
                    "questions": {
                        "type": "array",
                        "description": "Validated questions from validate_question",
                        "items": {"type": "object"},
                    },
                },
                "required": ["questions"],
            },
        )
        result = await AgentCoreLoop(
            llm_client=self.llm_client,
            tool_registry=tool_registry,
            recovery_engine=RecoveryEngine(),
            max_iterations=6,
            agent_level=PermissionLevel.CONTENT_GENERATE,
        ).run(
            system_prompt=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"请围绕 `{self._resolve_topic(params)}` 生成 {self._question_count(params)} 道练习题，"
                        f"难度为 {self._resolve_difficulty(params)}。"
                    ),
                }
            ],
        )
        batch_output = result.tool_results[-1].output if result.tool_results else {}
        return batch_output if isinstance(batch_output, dict) else {}

    async def _tool_generate_questions(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        del tool_input
        topic = self._resolve_topic(params)
        difficulty = self._resolve_difficulty(params)
        count = self._question_count(params)
        try:
            question_batch = await self.question_generator.generate_batch(
                topic=topic,
                difficulty=difficulty,
                count=count,
                learning_context=params.get("learningContext", {}),
            )
            return question_batch.model_dump(by_alias=True)
        except Exception:
            templates = [
                PracticeQuestion(
                    questionId="q1",
                    questionType="SINGLE_CHOICE",
                    stem=f"关于 `{topic}`，下列哪项最符合其核心概念？",
                    options=[
                        "只和存储空间有关",
                        "只影响前端渲染",
                        "与查询条件和访问路径密切相关",
                        "只在主键场景生效",
                    ],
                    answer="C",
                    knowledgeTags=[topic, "核心概念"],
                    difficultyLevel=difficulty,
                    explanation=f"{topic} 的核心在于理解访问路径与适用条件。",
                ),
                PracticeQuestion(
                    questionId="q2",
                    questionType="SINGLE_CHOICE",
                    stem=f"学习 `{topic}` 时，最容易导致错误的一项是？",
                    options=[
                        "忽略题目条件",
                        "背诵定义",
                        "查看例题",
                        "整理笔记",
                    ],
                    answer="A",
                    knowledgeTags=[topic, "易错点"],
                    difficultyLevel=difficulty,
                    explanation="很多错误来自没有先判断题目是否满足使用前提。",
                ),
                PracticeQuestion(
                    questionId="q3",
                    questionType="SHORT_ANSWER",
                    stem=f"请用自己的话说明 `{topic}` 的使用前提，并举一个容易误判的场景。",
                    answer="需要先判断题目条件是否满足使用前提，并结合具体查询场景说明容易误判的位置。",
                    knowledgeTags=[topic, "使用条件", "错因分析"],
                    difficultyLevel=difficulty,
                    explanation="回答应覆盖使用前提和误判场景两个部分。",
                ),
                PracticeQuestion(
                    questionId="q4",
                    questionType="SINGLE_CHOICE",
                    stem=f"如果你在 `{topic}` 相关题目中总做错，第一步最应该做什么？",
                    options=[
                        "直接记答案",
                        "先判断知识点适用条件",
                        "跳过这类题",
                        "只看结论",
                    ],
                    answer="B",
                    knowledgeTags=[topic, "解题步骤"],
                    difficultyLevel=difficulty,
                    explanation="先判断适用条件，再做后续推理。",
                ),
                PracticeQuestion(
                    questionId="q5",
                    questionType="SHORT_ANSWER",
                    stem=f"请给出一个你检查 `{topic}` 是否掌握的自测方法。",
                    answer="先复述定义，再判断一个具体场景是否满足使用条件，最后解释原因。",
                    knowledgeTags=[topic, "自测方法"],
                    difficultyLevel=difficulty,
                    explanation="回答要体现定义、条件判断和原因解释。",
                ),
            ]
            return {
                "title": f"{topic} 练习题",
                "topic": topic,
                "difficulty": difficulty,
                "questions": [
                    question.model_dump(by_alias=True)
                    for question in templates[:count]
                ],
            }

    def _tool_validate_question(self, tool_input: dict[str, Any]) -> dict[str, Any]:
        questions = [
            PracticeQuestion.model_validate(question)
            for question in tool_input.get("questions", [])
        ]
        validated_questions = [
            question.model_dump(by_alias=True)
            for question in questions
            if question.stem and question.answer and question.knowledge_tags
        ]
        return {
            "topic": tool_input.get("topic", "当前主题"),
            "difficulty": tool_input.get("difficulty", "MIXED"),
            "questions": validated_questions,
        }

    def _tool_format_question_batch(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
    ) -> dict[str, Any]:
        topic = str(tool_input.get("topic") or self._resolve_topic(params))
        difficulty = str(tool_input.get("difficulty") or self._resolve_difficulty(params))
        return QuestionBatchPayload(
            title=f"{topic} 练习题",
            topic=topic,
            difficulty=difficulty,
            questions=[
                PracticeQuestion.model_validate(question)
                for question in tool_input.get("questions", [])
            ],
        ).model_dump(by_alias=True)

    def _resolve_topic(self, params: dict[str, Any]) -> str:
        learning_context = params.get("learningContext", {})
        return str(
            params.get("topic")
            or params.get("query")
            or learning_context.get("chapter")
            or learning_context.get("course")
            or "当前主题"
        )

    def _resolve_difficulty(self, params: dict[str, Any]) -> str:
        return str(params.get("difficulty") or "MIXED")

    def _question_count(self, params: dict[str, Any]) -> int:
        count = int(params.get("count", 5))
        return max(1, min(count, 5))

    async def _safe_save_question_batch(
        self,
        *,
        user_id: str,
        task_id: str,
        question_batch: QuestionBatchPayload,
    ) -> dict[str, Any]:
        try:
            metadata = await self.practice_store.save_question_batch(
                user_id=user_id,
                batch=question_batch,
                task_id=task_id,
            )
            return metadata
        except Exception:
            return await self.fallback_practice_store.save_question_batch(
                user_id=user_id,
                batch=question_batch,
                task_id=task_id,
            )
