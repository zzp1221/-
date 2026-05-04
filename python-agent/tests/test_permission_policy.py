import pytest

from src.ai_modules.runtime import (
    AgentCoreLoop,
    AssistantTurn,
    PermissionLevel,
    PermissionPolicy,
    PermissionRule,
    ToolCall,
    ToolRegistry,
)


class MockLLM:
    def __init__(self, turns: list[AssistantTurn]) -> None:
        self.turns = turns
        self.calls = 0

    async def complete(self, *, system_prompt, messages, tools) -> AssistantTurn:
        del system_prompt, messages, tools
        turn = self.turns[self.calls]
        self.calls += 1
        return turn


@pytest.mark.asyncio
async def test_permission_policy_denies_by_agent_level() -> None:
    registry = ToolRegistry()
    registry.register(
        name="update_profile",
        fn=lambda tool_input: tool_input,
        permission_level=PermissionLevel.SYSTEM_WRITE,
        description="Update learner profile",
    )
    policy = PermissionPolicy()
    loop = AgentCoreLoop(
        llm_client=MockLLM(
            turns=[
                AssistantTurn(
                    content="尝试更新画像",
                    tool_calls=[
                        ToolCall(
                            id="call_profile",
                            name="update_profile",
                            input={"userId": "u1"},
                        )
                    ],
                ),
                AssistantTurn(content="权限不足，停止执行。"),
            ]
        ),
        tool_registry=registry,
        permission_policy=policy,
        max_iterations=3,
        agent_level=PermissionLevel.CONTENT_GENERATE,
    )

    result = await loop.run(
        system_prompt="test",
        messages=[{"role": "user", "content": "更新画像"}],
    )

    assert result.tool_results[0].is_error is True
    assert result.tool_results[0].output == "denied by level"
    assert policy.audit_log[-1]["allowed"] is False


@pytest.mark.asyncio
async def test_permission_policy_allows_by_level() -> None:
    registry = ToolRegistry()
    registry.register(
        name="generate_document",
        fn=lambda tool_input: {"ok": True, "topic": tool_input["topic"]},
        permission_level=PermissionLevel.CONTENT_GENERATE,
        description="Generate content",
    )
    policy = PermissionPolicy()
    loop = AgentCoreLoop(
        llm_client=MockLLM(
            turns=[
                AssistantTurn(
                    content="生成文档",
                    tool_calls=[
                        ToolCall(
                            id="call_generate",
                            name="generate_document",
                            input={"topic": "数据库索引"},
                        )
                    ],
                ),
                AssistantTurn(content="生成完成。"),
            ]
        ),
        tool_registry=registry,
        permission_policy=policy,
        max_iterations=3,
        agent_level=PermissionLevel.CONTENT_GENERATE,
    )

    result = await loop.run(
        system_prompt="test",
        messages=[{"role": "user", "content": "生成文档"}],
    )

    assert result.tool_results[0].is_error is False
    assert result.tool_results[0].output["ok"] is True
    assert policy.audit_log[-1]["reason"] == "allowed by level"


@pytest.mark.asyncio
async def test_permission_policy_deny_rule_overrides_level() -> None:
    registry = ToolRegistry()
    registry.register(
        name="write_file",
        fn=lambda tool_input: tool_input,
        permission_level=PermissionLevel.FILE_WRITE,
        description="Write file to sandbox",
    )
    policy = PermissionPolicy(
        deny_rules=[
            PermissionRule(
                toolName="write_file",
                pattern="path=/etc/*",
                action="deny",
            )
        ]
    )
    loop = AgentCoreLoop(
        llm_client=MockLLM(
            turns=[
                AssistantTurn(
                    content="写文件",
                    tool_calls=[
                        ToolCall(
                            id="call_write",
                            name="write_file",
                            input={"path": "/etc/passwd"},
                        )
                    ],
                ),
                AssistantTurn(content="规则拒绝。"),
            ]
        ),
        tool_registry=registry,
        permission_policy=policy,
        max_iterations=3,
        agent_level=PermissionLevel.FULL_ACCESS,
    )

    result = await loop.run(
        system_prompt="test",
        messages=[{"role": "user", "content": "写文件"}],
    )

    assert result.tool_results[0].is_error is True
    assert result.tool_results[0].output == "denied by rule"
    assert policy.audit_log[-1]["matched_rule"] == "deny:write_file:path=/etc/*"
