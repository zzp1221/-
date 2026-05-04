"""Permission policy for tool execution authorization."""

from __future__ import annotations

from enum import IntEnum
from fnmatch import fnmatch
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PermissionLevel(IntEnum):
    """Ordered permission levels for agents and tools."""

    READ_ONLY = 1
    CONTENT_GENERATE = 2
    FILE_WRITE = 3
    SYSTEM_WRITE = 4
    FULL_ACCESS = 5


class PermissionRule(BaseModel):
    """Pattern-based rule for authorization decisions."""

    tool_name: str = Field(alias="toolName")
    pattern: str | None = None
    action: Literal["allow", "deny"]  # ask deferred to later step

    model_config = ConfigDict(populate_by_name=True)

    def matches(self, tool_name: str, tool_input: dict[str, Any]) -> bool:
        if self.tool_name != tool_name:
            return False
        if self.pattern is None:
            return True

        flattened = " ".join(f"{key}={value}" for key, value in sorted(tool_input.items()))
        return fnmatch(flattened, self.pattern)


class PermissionDecision(BaseModel):
    """Resolved authorization decision."""

    allowed: bool
    reason: str
    matched_rule: str | None = Field(default=None, alias="matchedRule")

    model_config = ConfigDict(populate_by_name=True)


class PermissionPolicy:
    """Authorize tool execution using ordered rules and level checks."""

    def __init__(
        self,
        deny_rules: list[PermissionRule] | None = None,
        allow_rules: list[PermissionRule] | None = None,
    ) -> None:
        self.deny_rules = deny_rules or []
        self.allow_rules = allow_rules or []
        self.audit_log: list[dict[str, Any]] = []

    def authorize(
        self,
        *,
        tool_name: str,
        tool_input: dict[str, Any],
        agent_level: int,
        tool_required_level: int,
    ) -> PermissionDecision:
        for rule in self.deny_rules:
            if rule.matches(tool_name, tool_input):
                decision = PermissionDecision(
                    allowed=False,
                    reason="denied by rule",
                    matchedRule=f"deny:{rule.tool_name}:{rule.pattern}",
                )
                self._record(tool_name, tool_input, agent_level, tool_required_level, decision)
                return decision

        for rule in self.allow_rules:
            if rule.matches(tool_name, tool_input):
                decision = PermissionDecision(
                    allowed=True,
                    reason="allowed by rule",
                    matchedRule=f"allow:{rule.tool_name}:{rule.pattern}",
                )
                self._record(tool_name, tool_input, agent_level, tool_required_level, decision)
                return decision

        if agent_level >= tool_required_level:
            decision = PermissionDecision(
                allowed=True,
                reason="allowed by level",
            )
            self._record(tool_name, tool_input, agent_level, tool_required_level, decision)
            return decision

        decision = PermissionDecision(
            allowed=False,
            reason="denied by level",
        )
        self._record(tool_name, tool_input, agent_level, tool_required_level, decision)
        return decision

    def _record(
        self,
        tool_name: str,
        tool_input: dict[str, Any],
        agent_level: int,
        tool_required_level: int,
        decision: PermissionDecision,
    ) -> None:
        self.audit_log.append(
            {
                "tool_name": tool_name,
                "tool_input": dict(tool_input),
                "agent_level": agent_level,
                "tool_required_level": tool_required_level,
                "allowed": decision.allowed,
                "reason": decision.reason,
                "matched_rule": decision.matched_rule,
            }
        )
