"""从 SKILL.md 文件加载智能体提示词，不引入额外依赖。"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from src.ai_modules.runtime.context_snapshot import SnapshotBuilder, SystemSnapshot


@dataclass(frozen=True)
class SkillDocument:
    """解析后的 SKILL.md 内容，用于构建智能体系统提示词。"""

    name: str
    description: str
    body: str


class SkillPromptLoader:
    """从 python-agent/skills 渐进式读取智能体 Skill。"""

    def __init__(self, skills_root: Path | None = None) -> None:
        self.skills_root = skills_root or Path(__file__).resolve().parents[3] / "skills"

    def build_system_prompt(
        self,
        *,
        skill_name: str,
        snapshot: SystemSnapshot,
        fallback_prompt: str,
    ) -> str:
        skill = self.load(skill_name)
        if skill is None:
            return fallback_prompt

        snapshot_context = SnapshotBuilder.render_prompt_context(snapshot)
        body = skill.body.strip()
        if "{{snapshot_context}}" in body:
            return body.replace("{{snapshot_context}}", snapshot_context)
        return "\n\n".join([body, snapshot_context])

    def load(self, skill_name: str) -> SkillDocument | None:
        skill_path = self.skills_root / skill_name / "SKILL.md"
        return _load_skill_document(skill_path)


@lru_cache(maxsize=64)
def _load_skill_document(skill_path: Path) -> SkillDocument | None:
    try:
        raw = skill_path.read_text(encoding="utf-8")
    except OSError:
        return None

    frontmatter, body = _split_frontmatter(raw)
    name = frontmatter.get("name", "").strip()
    description = frontmatter.get("description", "").strip()
    if not name or not description or not body.strip():
        return None
    return SkillDocument(name=name, description=description, body=body)


def _split_frontmatter(raw: str) -> tuple[dict[str, str], str]:
    lines = raw.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, raw

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break
    if end_index is None:
        return {}, raw

    frontmatter: dict[str, str] = {}
    for line in lines[1:end_index]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip("\"'")
    body = "\n".join(lines[end_index + 1 :]).strip()
    return frontmatter, body
