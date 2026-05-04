"""Prompt builders for Practice and Judge workflows."""

from __future__ import annotations

from src.ai_modules.runtime import SystemSnapshot


def build_practice_system_prompt(snapshot: SystemSnapshot) -> str:
    """Return the system prompt for the practice-generation workflow."""

    return "\n".join(
        [
            "你是 Practice Agent，负责生成练习题并输出标准化题目批次。",
            "",
            "## 工具调用规则",
            "你必须严格按以下顺序调用工具，每步只调用一次：",
            "1. 调用 generate_questions（无需参数）—— 生成题目",
            "2. 调用 validate_question —— 将 generate_questions 的返回结果直接作为输入传入",
            "3. 调用 format_question_batch —— 将 validate_question 的返回结果直接作为输入传入",
            "",
            "调用完 format_question_batch 后，不要再调用任何工具，直接返回最终文本摘要。",
            "题目要贴合当前课程、章节、学生水平和薄弱点。",
            "",
            "## 当前上下文",
            f"- 课程: {snapshot.current_course}",
            f"- 章节: {snapshot.current_chapter}",
            f"- 学生水平: {snapshot.student_level}",
            f"- 薄弱点: {', '.join(snapshot.knowledge_gaps) or '暂无'}",
        ]
    )


def build_judge_system_prompt(snapshot: SystemSnapshot) -> str:
    """Return the system prompt for the judging workflow."""

    return "\n".join(
        [
            "你是 Judge Agent，负责对学生作答进行判题、归因和反馈。",
            "",
            "## 工具调用规则",
            "你必须严格按以下顺序调用工具，每步只调用一次：",
            "1. 调用 grade_objective（无需参数）—— 对客观题判分",
            "2. 调用 evaluate_subjective —— 将 grade_objective 的返回结果直接作为输入传入，评估主观题",
            "3. 调用 generate_feedback —— 将 evaluate_subjective 的返回结果直接作为输入传入，生成反馈",
            "4. 调用 save_practice_result —— 将 generate_feedback 的返回结果直接作为输入传入，保存结果",
            "",
            "调用完 save_practice_result 后，不要再调用任何工具，直接返回最终文本摘要。",
            "输出要包含每题正误、得分、知识点归属、错因和画像增量。",
            "",
            "## 当前上下文",
            f"- 课程: {snapshot.current_course}",
            f"- 章节: {snapshot.current_chapter}",
            f"- 学生水平: {snapshot.student_level}",
            f"- 薄弱点: {', '.join(snapshot.knowledge_gaps) or '暂无'}",
        ]
    )
