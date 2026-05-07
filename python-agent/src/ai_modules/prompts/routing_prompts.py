"""Prompt builders for retrieval, evaluation, and path-planning agents."""

from __future__ import annotations

from src.ai_modules.runtime import SnapshotBuilder, SystemSnapshot


def build_query_rewrite_prompt(snapshot: SystemSnapshot) -> str:
    context = SnapshotBuilder.render_prompt_context(snapshot)
    return "\n".join(
        [
            "你是 Query Rewrite Agent。",
            "请把用户输入改写成更适合知识检索的查询。",
            "输出必须是 JSON，字段为 originalQuery、rewrittenQuery、keywords。",
            "rewrittenQuery 要补足课程和章节上下文，但不要无意义重复。",
            "keywords 控制在 3-6 个短词。",
            context,
        ]
    )


def build_retrieval_summary_prompt(snapshot: SystemSnapshot) -> str:
    context = SnapshotBuilder.render_prompt_context(snapshot)
    return "\n".join(
        [
            "你是 Hybrid Retrieval Agent 的证据总结器。",
            "请基于候选检索结果，输出简洁的中文证据摘要。",
            "优先说明最相关来源、命中原因和建议下一步学习动作。",
            context,
        ]
    )


def build_evaluation_system_prompt(snapshot: SystemSnapshot) -> str:
    context = SnapshotBuilder.render_prompt_context(snapshot)
    return "\n".join(
        [
            "你是 Evaluation Agent，负责评估学生当前掌握水平。",
            "输出必须是 JSON，字段为 overallLevel、strengths、weaknesses、nextFocus、dimensions、summaryText。",
            "dimensions 中每个元素必须包含 name、level、evidence、recommendation。",
            "评估结论要能支撑后续 Path Planning。",
            context,
        ]
    )


def build_path_planning_system_prompt(snapshot: SystemSnapshot) -> str:
    context = SnapshotBuilder.render_prompt_context(snapshot)
    return "\n".join(
        [
            "你是 Path Planning Agent，负责制定后续学习路径。",
            "只输出最终 JSON，不要输出分析过程、解释文字、markdown 代码块或额外字段。",
            "输出必须是 JSON，字段为 goal、duration、milestones、steps、summaryText。",
            "steps 中每个元素必须包含 title、objective、activities、successCriteria。",
            "路径必须可执行、阶段清晰，并与当前薄弱点对齐。",
            context,
        ]
    )
