"""Prompt builders for critic and safety review workflows."""

from __future__ import annotations

from src.ai_modules.runtime import SnapshotBuilder, SystemSnapshot


def build_critic_system_prompt(snapshot: SystemSnapshot) -> str:
    context = SnapshotBuilder.render_prompt_context(snapshot)
    return "\n".join(
        [
            "你是 Critic Agent，负责复核教学资源内容质量。",
            "输出必须是 JSON，字段为 verdict、factConsistency、difficultyMatch、sourceCoverage、issues、suggestions、summaryText。",
            "请重点核对事实一致性、难度匹配度、来源覆盖度，并给出简洁可执行建议。",
            context,
        ]
    )


def build_safety_system_prompt(snapshot: SystemSnapshot) -> str:
    context = SnapshotBuilder.render_prompt_context(snapshot)
    return "\n".join(
        [
            "你是 Safety Agent，负责识别教学内容安全与合规风险。",
            "输出必须是 JSON，字段为 allowed、riskLevel、categories、riskTags、blockedReason、suggestions、summaryText。",
            "请重点识别越界内容、学术违规、作弊建议、危险操作和不适合学生当前水平的风险。",
            context,
        ]
    )
