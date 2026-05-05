from src.ai_modules.llms import OpenAICompatibleTutorLLM
from src.ai_modules.runtime import AssistantTurn, ToolCall, ToolExecutionResult


def test_openai_compatible_llm_normalizes_tool_call_roundtrip_messages() -> None:
    llm = OpenAICompatibleTutorLLM(api_key="test-key")
    assistant_message = AssistantTurn(
        content="",
        tool_calls=[
            ToolCall(
                id="call_001",
                name="read_retrieval_evidence",
                input={"topic": "联合索引"},
            )
        ],
    ).as_message()
    tool_message = ToolExecutionResult(
        toolCallId="call_001",
        toolName="read_retrieval_evidence",
        output={
            "query": "联合索引",
            "rewrittenQuery": "数据库原理 联合索引",
            "documents": [{"title": "联合索引与覆盖索引", "channel": "hybrid"}],
        },
        isError=False,
    ).as_message()

    normalized = llm._normalize_messages(
        [
            {"role": "user", "content": "请解释联合索引什么时候生效。"},
            assistant_message,
            tool_message,
        ]
    )

    assert normalized[1]["tool_calls"][0]["type"] == "function"
    assert normalized[1]["tool_calls"][0]["function"]["name"] == "read_retrieval_evidence"
    assert normalized[1]["tool_calls"][0]["function"]["arguments"] == '{"topic": "联合索引"}'
    assert normalized[2]["role"] == "tool"
    assert normalized[2]["tool_call_id"] == "call_001"
    assert '"rewrittenQuery": "数据库原理 联合索引"' in normalized[2]["content"]
