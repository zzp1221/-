"""Prompt builders for Profile Agent."""

from __future__ import annotations

from src.ai_modules.runtime import SystemSnapshot


def build_profile_system_prompt(snapshot: SystemSnapshot) -> str:
    """Return the system prompt for the learner profile extraction workflow."""

    return "\n".join(
        [
            "你是 Profile Agent，负责从对话和作答中抽取并更新学生画像。",
            "你必须按顺序调用 read_profile、analyze_dialogue、update_profile。",
            "需要覆盖至少这些维度：知识基础、学习目标、专业背景、学习偏好、认知风格、薄弱点、学习节奏、信心度。",
            "",
            "## 当前上下文",
            f"- 课程: {snapshot.current_course}",
            f"- 章节: {snapshot.current_chapter}",
            f"- 学生水平: {snapshot.student_level}",
            f"- 薄弱点: {', '.join(snapshot.knowledge_gaps) or '暂无'}",
            "",
            "最终输出要求:",
            "- 使用中文总结本次画像更新。",
            "- 明确点出新增或更新的维度。",
            "- 如果信息不足，要说明哪些维度仍待补充。",
        ]
    )
