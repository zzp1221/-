"""Evaluation agent backed by AgentCoreLoop and LLM-generated reports."""

from __future__ import annotations

from collections.abc import AsyncIterator
import logging
from typing import Any

from src.ai_modules.agents.base import PlaceholderAgent
from src.ai_modules.llms import EvaluationGenerator, PlanningLLMClientFactory, PracticeQuestionGenerator
from src.ai_modules.models import (
    EvaluationDimension,
    EvaluationPayload,
    PracticeQuestion,
    ProgressPayload,
    ProgressSSEEvent,
    QuestionBatchPayload,
    QuestionBatchSSEEvent,
    ResourceFilePayload,
    ResourceFileSSEEvent,
    ResultChunkPayload,
    ResultChunkSSEEvent,
    SSEEvent,
)
from src.ai_modules.prompts import build_evaluation_system_prompt
from src.ai_modules.runtime import (
    SystemSnapshot,
)

LOGGER = logging.getLogger(__name__)
INTERACTIVE_DIMENSIONS = {"案例迁移", "练习掌握", "学习主动性", "复盘闭环"}


class EvaluationAgent(PlaceholderAgent):
    """Evaluate learner readiness and feed planning context."""

    def __init__(
        self,
        llm_client: Any | None = None,
        generator: Any | None = None,
        question_generator: Any | None = None,
    ) -> None:
        super().__init__("Evaluation Agent", "evaluation")
        self.llm_client = llm_client or PlanningLLMClientFactory.create()
        self.generator = generator
        self.question_generator = question_generator or PracticeQuestionGenerator()

    def system_prompt(self, snapshot: SystemSnapshot) -> str:
        return build_evaluation_system_prompt(snapshot)

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
        del service_type
        payload = await self._run_agent_core_loop(
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
        )
        primary_dimension = self._resolve_primary_dimension(params)
        params["evaluationResult"] = payload.model_dump(by_alias=True)
        params["profileSource"] = "EVALUATION"
        report_markdown = self._render_dimension_report(
            dimension=primary_dimension,
            payload=payload,
            params=params,
            snapshot=snapshot,
        )
        question_batch = await self._build_practice_question_batch(
            dimension=primary_dimension,
            payload=payload,
            params=params,
            snapshot=snapshot,
        )
        if question_batch is not None:
            params["practiceQuestionBatch"] = question_batch.model_dump(by_alias=True)
            params["practiceQuestions"] = [
                question.model_dump(by_alias=True)
                for question in question_batch.questions
            ]

        yield ProgressSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq,
            payload=ProgressPayload(
                stage=self.stage_name,
                percent=45,
                message=f"已完成{primary_dimension}专项评估",
            ),
        )
        yield ResourceFileSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 1,
            payload=ResourceFilePayload(
                assetType="DOCUMENT",
                title=f"{primary_dimension}专项评估",
                summary=payload.summary_text,
                displayMode="INLINE_MARKDOWN",
                fileName="",
                localPath=None,
                mimeType="text/markdown; charset=UTF-8",
                inlineContent=report_markdown,
            ),
        )
        yield ResultChunkSSEEvent(
            taskId=task_id,
            traceId=trace_id,
            seq=seq + 2,
            payload=ResultChunkPayload(text=self._build_dimension_summary(primary_dimension, payload, question_batch)),
        )
        if question_batch is not None:
            yield QuestionBatchSSEEvent(
                taskId=task_id,
                traceId=trace_id,
                seq=seq + 3,
                payload=question_batch,
            )

    async def _run_agent_core_loop(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> EvaluationPayload:
        aggregated = self._tool_aggregate_behavior(tool_input={}, params=params, snapshot=snapshot)
        return await self._safe_evaluate(
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
            aggregated_behavior=aggregated,
        )

    def _tool_aggregate_behavior(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> dict[str, Any]:
        del tool_input
        profile = params.get("profile", {})
        evaluation = params.get("evaluationResult", {})
        judge_result = params.get("judgeResult", {})
        messages = params.get("messages", [])
        structured_summary = params.get("structuredConversationSummary", {})

        weaknesses = self._unique_items(
            [
                *list(profile.get("knowledgeGaps", [])),
                *list(evaluation.get("weaknesses", [])),
                *list(judge_result.get("weakKnowledgeTags", [])),
                *list(snapshot.knowledge_gaps),
            ]
        )
        focus = self._unique_items(
            [
                *list(evaluation.get("nextFocus", [])),
                *weaknesses[:3],
                snapshot.current_chapter,
            ]
        )
        strengths = self._unique_items(
            [
                *list(evaluation.get("strengths", [])),
                "愿意持续练习" if params.get("practiceQuestionBatch") else "",
                "具备学习上下文" if params.get("learningContext") else "",
                "最近有复习记录" if snapshot.recent_activities else "",
            ]
        )
        learner_messages = [
            str(message.get("content", ""))
            for message in messages
            if isinstance(message, dict) and message.get("role") == "user"
        ]
        aggregated = {
            "profile": profile,
            "learningContext": params.get("learningContext", {}),
            "judgeResult": judge_result,
            "messages": messages,
            "structuredConversationSummary": structured_summary,
            "snapshot": {
                "studentLevel": snapshot.student_level,
                "knowledgeGaps": snapshot.knowledge_gaps,
                "recentMistakes": snapshot.recent_mistakes,
                "preferredStyle": snapshot.preferred_style,
            },
            "behaviorSignals": {
                "messageCount": len(messages),
                "learnerQuestionCount": len(learner_messages),
                "recentMistakeCount": len(snapshot.recent_mistakes),
                "practiceAccuracy": judge_result.get("accuracy"),
                "conversationKeywords": learner_messages[-3:],
            },
            "candidateStrengths": strengths or ["愿意配合学习"],
            "candidateWeaknesses": weaknesses or ["薄弱点待补充"],
            "recommendedFocus": focus or ["核心概念", "适用条件"],
        }
        params["aggregatedEvaluationContext"] = aggregated
        return aggregated

    async def _tool_generate_report(
        self,
        *,
        tool_input: dict[str, Any],
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
    ) -> dict[str, Any]:
        aggregated = params.get("aggregatedEvaluationContext") or tool_input
        payload = await self._safe_evaluate(
            params=params,
            snapshot=snapshot,
            system_prompt=system_prompt,
            aggregated_behavior=aggregated if isinstance(aggregated, dict) else {},
        )
        return payload.model_dump(by_alias=True)

    async def _safe_evaluate(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        system_prompt: str,
        aggregated_behavior: dict[str, Any],
    ) -> EvaluationPayload:
        generator = self.generator or EvaluationGenerator()
        try:
            return await generator.evaluate(
                system_prompt=system_prompt,
                context_payload=self._build_context_payload(
                    params=params,
                    snapshot=snapshot,
                    aggregated_behavior=aggregated_behavior,
                ),
            )
        except Exception as exc:
            LOGGER.exception("Evaluation LLM failed")
            raise RuntimeError("Evaluation LLM failed") from exc

    def _build_context_payload(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        aggregated_behavior: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "profile": params.get("profile", {}),
            "learningContext": params.get("learningContext", {}),
            "assessmentRange": params.get("range"),
            "assessmentDimensions": params.get("dimensions", []),
            "judgeResult": params.get("judgeResult", {}),
            "messages": params.get("messages", []),
            "snapshot": {
                "studentLevel": snapshot.student_level,
                "knowledgeGaps": snapshot.knowledge_gaps,
                "recentMistakes": snapshot.recent_mistakes,
                "preferredStyle": snapshot.preferred_style,
            },
            "aggregatedBehavior": aggregated_behavior,
        }

    def _resolve_primary_dimension(self, params: dict[str, Any]) -> str:
        dimensions = params.get("dimensions")
        if isinstance(dimensions, list):
            for item in dimensions:
                text = str(item).strip()
                if text:
                    return text
        text = str(params.get("assessmentDimension") or "").strip()
        return text or "知识基础"

    async def _build_practice_question_batch(
        self,
        *,
        dimension: str,
        payload: EvaluationPayload,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> QuestionBatchPayload | None:
        topic = self._resolve_assessment_topic(params, snapshot, payload)
        difficulty = self._resolve_practice_difficulty(payload, snapshot)
        focus_items = self._resolve_focus_items(payload, snapshot)
        learning_context = params.get("learningContext", {})
        if dimension == "练习掌握":
            try:
                generated = await self.question_generator.generate_batch(
                    topic=topic,
                    difficulty=difficulty,
                    count=3,
                    learning_context=learning_context if isinstance(learning_context, dict) else {},
                )
                return generated.model_copy(
                    update={
                        "description": "系统已围绕当前薄弱点生成 1-3 道测评题，请直接作答后查看掌握判断。",
                        "assessment_dimension": dimension,
                        "submit_label": "提交掌握评估",
                    }
                )
            except Exception:
                LOGGER.warning("Failed to generate practice assessment batch, falling back to deterministic questions", exc_info=True)
                questions = [
                    PracticeQuestion(
                        questionId="assessment-q1",
                        questionType="SINGLE_CHOICE",
                        stem=f"关于“{topic}”，下列哪项最能体现你是否真正掌握了核心概念？",
                        options=[
                            "只会背定义",
                            "能判断适用条件并解释原因",
                            "只记住例题答案",
                            "只知道结论但不会推导",
                        ],
                        answer="B",
                        knowledgeTags=[topic, "核心概念"],
                        difficultyLevel=difficulty,
                        explanation="真正掌握意味着不仅记住概念，还能判断何时使用以及为什么使用。",
                    ),
                    PracticeQuestion(
                        questionId="assessment-q2",
                        questionType="SINGLE_CHOICE",
                        stem=f"如果题目场景发生变化，检验“{topic}”掌握情况时最关键的一步是什么？",
                        options=[
                            "直接套模板",
                            "先看别人答案",
                            "先判断场景是否满足使用前提",
                            "忽略限制条件",
                        ],
                        answer="C",
                        knowledgeTags=[topic, "适用条件", "迁移判断"],
                        difficultyLevel=difficulty,
                        explanation="先判断适用条件，才能说明你掌握的不是死记硬背，而是真理解。",
                    ),
                    PracticeQuestion(
                        questionId="assessment-q3",
                        questionType="SHORT_ANSWER",
                        stem=f"请用自己的话说明“{topic}”最容易做错的一步，并给出你的改正策略。",
                        answer="先指出最容易忽略的条件或判断步骤，再说明你会如何检查并修正。",
                        knowledgeTags=[topic, "错因分析", "复盘策略"],
                        difficultyLevel=difficulty,
                        explanation="回答需同时体现错因识别和纠错策略，才能反映真实掌握情况。",
                    ),
                ]
                return QuestionBatchPayload(
                    title=f"{topic} 练习掌握专项评估",
                    topic=topic,
                    difficulty=difficulty,
                    description="系统已围绕当前薄弱点生成 1-3 道测评题，请直接作答后查看掌握判断。",
                    assessmentDimension=dimension,
                    submitLabel="提交掌握评估",
                    questions=questions,
                )
        if dimension == "案例迁移":
            focus = focus_items[0]
            transfer_scene = self._resolve_transfer_scene(params, snapshot)
            return QuestionBatchPayload(
                title=f"{topic} 案例迁移专项评估",
                topic=topic,
                difficulty=difficulty,
                description="请把当前知识点迁移到新场景中判断适用条件，系统会根据你的分析过程评估迁移能力。",
                assessmentDimension=dimension,
                submitLabel="提交迁移分析",
                questions=[
                    PracticeQuestion(
                        questionId="transfer-q1",
                        questionType="SINGLE_CHOICE",
                        stem=f"如果把“{focus}”放到“{transfer_scene}”这个新场景中，第一步最应该做什么？",
                        options=[
                            "直接沿用原题解法",
                            "先判断新场景是否满足使用前提",
                            "只看结论是否相似",
                            "优先背诵定义避免出错",
                        ],
                        answer="B",
                        knowledgeTags=[topic, focus, "案例迁移"],
                        difficultyLevel=difficulty,
                        explanation="迁移评估核心看你是否会先检查新场景与原知识点的适用条件是否一致。",
                    ),
                    PracticeQuestion(
                        questionId="transfer-q2",
                        questionType="SHORT_ANSWER",
                        stem=f"请说明“{focus}”在“{transfer_scene}”中能否直接使用，并写出你判断时会检查的两个条件。",
                        answer="先明确能否直接使用，再至少写出两个判断条件，例如输入限制、前置依赖、边界条件或目标是否一致。",
                        knowledgeTags=[topic, focus, "条件判断", "迁移说明"],
                        difficultyLevel=difficulty,
                        explanation="回答需要同时体现结论和判断依据，才能说明你具备迁移能力。",
                    ),
                    PracticeQuestion(
                        questionId="transfer-q3",
                        questionType="SHORT_ANSWER",
                        stem=f"请你自拟一个与“{topic}”相近但不完全相同的新案例，并说明你会如何调整原来的思路。",
                        answer="需给出一个新案例，并说明与原案例的不同点，再写出至少一条思路调整或校验步骤。",
                        knowledgeTags=[topic, "案例迁移", "策略调整"],
                        difficultyLevel=difficulty,
                        explanation="真正的迁移不是复述旧题，而是能针对新约束调整方法。",
                    ),
                ],
            )
        if dimension == "学习主动性":
            focus = focus_items[0]
            return QuestionBatchPayload(
                title=f"{topic} 学习主动性专项评估",
                topic=topic,
                difficulty=difficulty,
                description="请结合你下一轮学习计划作答，系统会根据目标拆解、验证方式和主动提问意识评估你的主动性。",
                assessmentDimension=dimension,
                submitLabel="提交主动性计划",
                questions=[
                    PracticeQuestion(
                        questionId="initiative-q1",
                        questionType="SINGLE_CHOICE",
                        stem=f"当你发现自己在“{focus}”上理解不稳时，最能体现学习主动性的做法是哪一项？",
                        options=[
                            "等系统再次推送答案",
                            "先写出薄弱点、验证方式和准备追问的问题",
                            "直接跳过这个知识点",
                            "只收藏资料，不安排自测",
                        ],
                        answer="B",
                        knowledgeTags=[topic, focus, "学习主动性"],
                        difficultyLevel=difficulty,
                        explanation="主动学习不是等待内容，而是先定义目标、验证和提问。",
                    ),
                    PracticeQuestion(
                        questionId="initiative-q2",
                        questionType="SHORT_ANSWER",
                        stem=f"请写出你下一次学习“{topic}”时的 3 步主动学习计划，至少包含：先补什么、怎么验证、卡住时问什么。",
                        answer="答案应包含明确补强目标、一个可执行的验证动作，以及至少一个准备主动提出的问题。",
                        knowledgeTags=[topic, "学习计划", "主动提问"],
                        difficultyLevel=difficulty,
                        explanation="回答越具体，越能反映你是否形成了主动学习闭环。",
                    ),
                    PracticeQuestion(
                        questionId="initiative-q3",
                        questionType="SHORT_ANSWER",
                        stem="如果这轮学习结束后效果仍不理想，你会如何调整资源选择或练习方式？",
                        answer="需要说明至少一项调整动作，例如更换资源类型、缩小目标范围、增加自测频率或补做案例。",
                        knowledgeTags=[topic, "策略调整", "学习主动性"],
                        difficultyLevel=difficulty,
                        explanation="主动性不仅体现在开始阶段，也体现在效果不佳时是否会主动调整策略。",
                    ),
                ],
            )
        if dimension == "复盘闭环":
            focus = focus_items[0]
            recent_mistake = self._resolve_recent_mistake(snapshot, focus)
            return QuestionBatchPayload(
                title=f"{topic} 复盘闭环专项评估",
                topic=topic,
                difficulty=difficulty,
                description="请围绕最近一次错误或薄弱点完成复盘，系统会重点判断你是否能形成“错误原因 -> 改正动作 -> 再验证”的闭环。",
                assessmentDimension=dimension,
                submitLabel="提交复盘结果",
                questions=[
                    PracticeQuestion(
                        questionId="review-q1",
                        questionType="SHORT_ANSWER",
                        stem=f"请回顾最近一次与“{recent_mistake}”相关的失误，写出真正的错误原因，而不是只写“粗心”。",
                        answer="需要指出具体错因，例如忽略条件、概念混淆、步骤顺序错误、没有验证边界或复习不充分。",
                        knowledgeTags=[topic, focus, "错因分析"],
                        difficultyLevel=difficulty,
                        explanation="复盘的关键是找到真正原因，而不是只给出笼统结论。",
                    ),
                    PracticeQuestion(
                        questionId="review-q2",
                        questionType="SINGLE_CHOICE",
                        stem=f"如果下次再遇到“{focus}”相关题目，最能形成复盘闭环的第一步是什么？",
                        options=[
                            "先做完再说",
                            "先核对自己上次的错因，并按检查清单验证",
                            "直接背标准答案",
                            "只看别人讲解，不再自己作答",
                        ],
                        answer="B",
                        knowledgeTags=[topic, focus, "复盘闭环"],
                        difficultyLevel=difficulty,
                        explanation="真正的闭环是把上次的错因转成下一次作答前的检查动作。",
                    ),
                    PracticeQuestion(
                        questionId="review-q3",
                        questionType="SHORT_ANSWER",
                        stem=f"请为“{focus}”写一个 2-3 步的纠错检查清单，说明你下次做题前/做题后会怎么验证自己不再犯同类错误。",
                        answer="答案应包含至少两个可执行检查动作，并覆盖做题前的预判或做题后的复查。",
                        knowledgeTags=[topic, focus, "检查清单", "复盘闭环"],
                        difficultyLevel=difficulty,
                        explanation="只有把改正动作写成可执行步骤，复盘才算形成闭环。",
                    ),
                ],
            )
        return None

    def _resolve_assessment_topic(
        self,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        payload: EvaluationPayload,
    ) -> str:
        learning_context = params.get("learningContext", {})
        if isinstance(learning_context, dict):
            for key in ("chapter", "course"):
                value = str(learning_context.get(key) or "").strip()
                if value:
                    return value
        for candidate in (
            *payload.next_focus,
            snapshot.current_chapter,
            *(snapshot.knowledge_gaps or []),
        ):
            text = str(candidate or "").strip()
            if text:
                return text
        return "当前主题"

    def _resolve_practice_difficulty(self, payload: EvaluationPayload, snapshot: SystemSnapshot) -> str:
        level = str(payload.overall_level or snapshot.student_level or "BASIC").upper()
        if level in {"BEGINNER", "BASIC"}:
            return "BASIC"
        if level in {"ADVANCED", "EXPERT"}:
            return "ADVANCED"
        return "INTERMEDIATE"

    def _build_dimension_summary(
        self,
        dimension: str,
        payload: EvaluationPayload,
        question_batch: QuestionBatchPayload | None,
    ) -> str:
        if question_batch is not None:
            return (
                f"{dimension}专项评估已完成初步诊断，并生成 {len(question_batch.questions)} 道互动评估题。"
                "请直接在页面作答，系统会结合你的作答过程给出更准确的专项判断。"
            )
        return f"{dimension}专项评估已完成。{payload.summary_text}"

    def _render_dimension_report(
        self,
        *,
        dimension: str,
        payload: EvaluationPayload,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> str:
        strengths = self._markdown_list(payload.strengths[:3])
        weaknesses = self._markdown_list(payload.weaknesses[:3])
        next_focus = self._markdown_list(payload.next_focus[:3])
        dimension_lines = self._render_dimension_specific_lines(dimension, payload, params, snapshot)
        return "\n\n".join(
            section
            for section in [
                f"# {dimension}专项评估",
                "\n".join(
                    [
                        "## 评估结论",
                        f"- 当前等级：{payload.overall_level}",
                        f"- 评估周期：{params.get('range') or '近阶段'}",
                        f"- 综合判断：{payload.summary_text}",
                    ]
                ),
                "\n".join(["## 当前优势", *strengths]),
                "\n".join(["## 当前薄弱点", *weaknesses]),
                "\n".join(["## 下一步重点", *next_focus]),
                "\n".join(dimension_lines),
            ]
            if section
        )

    def _render_dimension_specific_lines(
        self,
        dimension: str,
        payload: EvaluationPayload,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
    ) -> list[str]:
        focus = payload.next_focus[:2] or payload.weaknesses[:2] or ["核心概念"]
        recent_mistakes = [str(item).strip() for item in snapshot.recent_mistakes if str(item).strip()]
        behavior = params.get("aggregatedEvaluationContext", {}).get("behaviorSignals", {})
        if dimension == "知识基础":
            return [
                "## 专项判断",
                f"- 当前更像是“概念未建立”而不是“做题粗心”，需先补齐 {focus[0]} 等基础知识。",
                "- 推荐先用定义复述 + 适用条件判断的方式完成基础校准。",
                "## 建议自检",
                f"- 你能否不看资料解释“{focus[0]}”的定义、作用与适用场景？",
                f"- 如果把“{focus[0]}”换一个题目场景，你还能判断它为什么成立吗？",
            ]
        if dimension == "案例迁移":
            return [
                "## 专项判断",
                f"- 当前重点不是继续背概念，而是把 {focus[0]} 迁移到新案例中判断适用条件。",
                "- 评估应关注你能否识别题目变化后仍保持正确解题思路。",
                "## 迁移检核",
                f"- 请尝试说明：如果题干条件变化，{focus[0]} 还能否直接套用？为什么？",
                f"- 你能否给出一个和当前知识点相似但不完全相同的新场景？",
            ]
        if dimension == "学习主动性":
            return [
                "## 专项判断",
                f"- 最近交互次数：{behavior.get('messageCount') or 0}，学习者主动提问次数：{behavior.get('learnerQuestionCount') or 0}。",
                "- 该维度优先看是否会主动拆问题、追问原因、提出下一步学习动作，而不是只等答案。",
                "## 主动性提示",
                "- 你下一轮学习前，应先写出“我要补什么、怎么验证、不会时问什么”。",
                "- 如果始终只有被动接收内容，说明主动性还没有形成闭环。",
            ]
        if dimension == "复盘闭环":
            return [
                "## 专项判断",
                f"- 最近错误记录：{', '.join(recent_mistakes[:3]) or '暂无显式错题记录'}。",
                "- 该维度关注你是否会把旧错转成纠错策略，而不是重复犯同类错误。",
                "## 复盘检核",
                "- 请先说出最近一次错误的真正原因，再说明下次你打算如何避免。",
                f"- 如果再次遇到 {focus[0]} 相关题目，你会先检查哪一步？",
            ]
        return [
            "## 专项判断",
            f"- 当前围绕 {focus[0]}、{focus[1] if len(focus) > 1 else focus[0]} 进行练习掌握评估。",
            "- 页面下方已生成专项测评题，作答后会返回更准确的掌握结论。",
        ]

    def _resolve_focus_items(self, payload: EvaluationPayload, snapshot: SystemSnapshot) -> list[str]:
        candidates = self._unique_items(
            [
                *payload.next_focus,
                *payload.weaknesses,
                *snapshot.knowledge_gaps,
                snapshot.current_chapter,
                "核心概念",
            ]
        )
        return candidates or ["核心概念"]

    def _resolve_transfer_scene(self, params: dict[str, Any], snapshot: SystemSnapshot) -> str:
        learning_context = params.get("learningContext", {})
        if isinstance(learning_context, dict):
            chapter = str(learning_context.get("chapter") or "").strip()
            course = str(learning_context.get("course") or "").strip()
            if chapter and course:
                return f"{course} 的 {chapter} 变式场景"
            if chapter:
                return f"{chapter} 的实际应用场景"
            if course:
                return f"{course} 的综合应用场景"
        if snapshot.current_chapter:
            return f"{snapshot.current_chapter} 的综合应用场景"
        return "新的实际应用场景"

    def _resolve_recent_mistake(self, snapshot: SystemSnapshot, fallback: str) -> str:
        for item in snapshot.recent_mistakes:
            text = str(item or "").strip()
            if text:
                return text
        return fallback

    def _markdown_list(self, items: list[str]) -> list[str]:
        normalized = [f"- {item}" for item in items if str(item).strip()]
        return normalized or ["- 暂无明显信号"]

    def _fallback_evaluation(
        self,
        *,
        params: dict[str, Any],
        snapshot: SystemSnapshot,
        aggregated_behavior: dict[str, Any] | None = None,
    ) -> EvaluationPayload:
        profile = params.get("profile", {})
        gaps = self._unique_items(
            [
                *list(profile.get("knowledgeGaps", [])),
                *list((aggregated_behavior or {}).get("candidateWeaknesses", [])),
                *list(snapshot.knowledge_gaps),
            ]
        )
        level = str(profile.get("studentLevel") or snapshot.student_level or "BASIC")
        focus = self._unique_items(
            list((aggregated_behavior or {}).get("recommendedFocus", [])) or gaps[:3]
        )
        strengths = self._unique_items(
            list((aggregated_behavior or {}).get("candidateStrengths", []))
        )
        dimensions = [
            EvaluationDimension(
                name="knowledge_foundation",
                level=level,
                evidence=f"当前识别到的薄弱点: {', '.join(gaps) or '暂无'}",
                recommendation="优先复习核心概念和适用条件。",
            ),
            EvaluationDimension(
                name="problem_solving",
                level="BASIC" if gaps else "INTERMEDIATE",
                evidence=f"近期错误: {', '.join(snapshot.recent_mistakes) or '暂无'}",
                recommendation="做题前先判断条件，再给出理由。",
            ),
        ]
        return EvaluationPayload(
            overallLevel=level,
            strengths=strengths or ["愿意配合练习", "具备基础学习上下文"],
            weaknesses=gaps or ["薄弱点待补充"],
            nextFocus=focus or ["核心概念", "适用条件"],
            dimensions=dimensions,
            summaryText=(
                f"当前评估等级为 {level}，"
                f"建议优先聚焦 {', '.join((focus or gaps[:3])[:3]) or '核心概念与适用条件'}。"
            ),
        )

    def _unique_items(self, items: list[Any]) -> list[str]:
        seen: set[str] = set()
        normalized: list[str] = []
        for item in items:
            text = str(item).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            normalized.append(text)
        return normalized
