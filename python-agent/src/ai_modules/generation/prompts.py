"""Prompt builders for structured resource generation."""

from __future__ import annotations

from typing import Any


def build_document_system_prompt() -> str:
    """Return the system prompt for structured teaching-content generation."""

    return (
        "你是一个严谨的教学内容生成助手。"
        "你必须基于提供的课程上下文、学生画像和检索来源生成结构化中文教学文档。"
        "优先保证正确性、条理性和教学可执行性，不要编造未给出的事实来源。"
        "输出必须是 JSON，对象结构为 "
        '{"sections":[{"title":"...","body":"...","tips":["..."],"citations":["..."]}]}.'
    )


def build_document_user_prompt(
    *,
    title: str,
    topic: str,
    snapshot: dict[str, Any],
    section_plans: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> str:
    """Build the user prompt for the structured document generation request."""

    source_lines = [
        (
            f"- 标题: {source.get('title', '未知来源')}; "
            f"渠道: {source.get('channel', 'unknown')}; "
            f"证据: {source.get('evidence', '无')}"
        )
        for source in sources[:5]
    ] or ["- 暂无稳定来源，请谨慎生成并保持表述保守。"]

    section_lines = [
        (
            f"- 标题: {plan.get('title', '')}; "
            f"目标: {plan.get('objective', '')}; "
            f"可用来源: {', '.join(plan.get('sourceTitles', [])) or '暂无'}"
        )
        for plan in section_plans
    ]

    return "\n".join(
        [
            f"文档标题: {title}",
            f"核心主题: {topic}",
            "",
            "学生与课程上下文:",
            f"- 课程: {snapshot.get('current_course', '未指定课程')}",
            f"- 章节: {snapshot.get('current_chapter', '未指定章节')}",
            f"- 学生水平: {snapshot.get('student_level', 'UNKNOWN')}",
            f"- 学习风格: {snapshot.get('preferred_style', 'step_by_step')}",
            f"- 薄弱点: {', '.join(snapshot.get('knowledge_gaps', [])) or '暂无'}",
            "",
            "请按以下大纲生成章节正文:",
            *section_lines,
            "",
            "可引用来源:",
            *source_lines,
            "",
            "生成要求:",
            "- 每个 section 都要写出完整正文，不能只重复标题。",
            "- tips 需要是学生可执行的学习建议。",
            "- citations 必须优先引用给定来源标题。",
            "- 若来源不足，表述保持保守，避免编造具体事实。",
        ]
    )


def build_reading_system_prompt() -> str:
    return (
        "你是一个严谨的教学阅读材料生成助手。"
        "你必须基于课程上下文、学生画像和检索来源生成中文延伸阅读材料。"
        "输出必须是 JSON，对象结构为 "
        '{"title":"...","summary":"...","body":"..."}。'
    )


def build_reading_user_prompt(
    *,
    title: str,
    topic: str,
    snapshot: dict[str, Any],
    sources: list[dict[str, Any]],
) -> str:
    source_lines = [
        (
            f"- 标题: {source.get('title', '未知来源')}; "
            f"渠道: {source.get('channel', 'unknown')}; "
            f"证据: {source.get('evidence', '无')}"
        )
        for source in sources[:5]
    ] or ["- 暂无稳定来源，请保持表述保守。"]
    return "\n".join(
        [
            f"材料标题: {title}",
            f"主题: {topic}",
            f"课程: {snapshot.get('current_course', '未指定课程')}",
            f"学生水平: {snapshot.get('student_level', 'UNKNOWN')}",
            f"学习风格: {snapshot.get('preferred_style', 'step_by_step')}",
            f"薄弱点: {', '.join(snapshot.get('knowledge_gaps', [])) or '暂无'}",
            "",
            "可引用来源:",
            *source_lines,
            "",
            "生成要求:",
            "- body 需要是完整的中文阅读材料，不是列表拼接。",
            "- 必须包含阅读目标、关键概念、易错提醒和阅读建议。",
            "- 若来源不足，保持保守，不要编造事实。",
        ]
    )


def build_slides_system_prompt() -> str:
    return (
        "你是一个教学 PPT 大纲生成助手。"
        "请生成适合授课的幻灯片大纲。"
        "输出必须是 JSON，对象结构为 "
        '{"title":"...","summary":"...","slides":[{"title":"...","bullets":["..."],"speakerNotes":"..."}]}.'
    )


def build_slides_user_prompt(
    *,
    title: str,
    topic: str,
    snapshot: dict[str, Any],
    sources: list[dict[str, Any]],
) -> str:
    source_lines = [
        f"- {source.get('title', '未知来源')}: {source.get('evidence', '无')}"
        for source in sources[:5]
    ] or ["- 暂无稳定来源，请保持概括性表达。"]
    return "\n".join(
        [
            f"PPT标题: {title}",
            f"主题: {topic}",
            f"课程: {snapshot.get('current_course', '未指定课程')}",
            f"章节: {snapshot.get('current_chapter', '未指定章节')}",
            f"学生水平: {snapshot.get('student_level', 'UNKNOWN')}",
            "",
            "可引用来源:",
            *source_lines,
            "",
            "生成要求:",
            "- 生成 5-7 页幻灯片。",
            "- 每页 bullets 必须可直接用于展示。",
            "- speakerNotes 要说明这一页如何讲解。",
        ]
    )


def build_mindmap_system_prompt() -> str:
    return (
        "你是一个教学思维导图生成助手。"
        "请输出 JSON，对象结构为 "
        '{"title":"...","summary":"...","root":"...","children":[{"name":"...","children":[{"name":"..."}]}]}.'
    )


def build_mindmap_user_prompt(
    *,
    title: str,
    topic: str,
    snapshot: dict[str, Any],
    sources: list[dict[str, Any]],
) -> str:
    source_lines = [
        f"- {source.get('title', '未知来源')}: {source.get('evidence', '无')}"
        for source in sources[:5]
    ] or ["- 暂无稳定来源，请保持结构化概括。"]
    return "\n".join(
        [
            f"导图标题: {title}",
            f"主题: {topic}",
            f"课程: {snapshot.get('current_course', '未指定课程')}",
            f"薄弱点: {', '.join(snapshot.get('knowledge_gaps', [])) or '暂无'}",
            "",
            "可引用来源:",
            *source_lines,
            "",
            "生成要求:",
            "- 根节点下至少 3 个一级分支。",
            "- 每个一级分支尽量有 2-4 个二级分支。",
            "- 结构要体现概念、原理、误区、练习或迁移。",
        ]
    )


def build_code_system_prompt() -> str:
    return (
        "你是一个教学代码案例生成助手。"
        "你必须生成可以阅读和学习的 Python 示例。"
        "输出必须是 JSON，对象结构为 "
        '{"title":"...","summary":"...","code":"...","explanation":"..."}。'
    )


def build_code_user_prompt(
    *,
    title: str,
    topic: str,
    snapshot: dict[str, Any],
    sources: list[dict[str, Any]],
) -> str:
    source_lines = [
        f"- {source.get('title', '未知来源')}: {source.get('evidence', '无')}"
        for source in sources[:5]
    ] or ["- 暂无稳定来源，请生成保守的演示性代码。"]
    return "\n".join(
        [
            f"代码案例标题: {title}",
            f"主题: {topic}",
            f"课程: {snapshot.get('current_course', '未指定课程')}",
            f"学生水平: {snapshot.get('student_level', 'UNKNOWN')}",
            "",
            "可引用来源:",
            *source_lines,
            "",
            "生成要求:",
            "- code 必须是完整的 Python 示例。",
            "- explanation 需要解释代码如何对应当前知识点。",
            "- 不要依赖复杂第三方库。",
        ]
    )
