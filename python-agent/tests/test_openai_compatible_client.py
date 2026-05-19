import pytest

from src.ai_modules.llms.openai_compatible import (
    OpenAICompatibleClient,
    extract_json_object_from_text,
)


def test_extract_json_object_from_text_prefers_fenced_final_object() -> None:
    mixed_output = """
推理草稿:
{"topic":"联合索引","attempt":1}

最终答案:
```json
{"title":"联合索引导学","summary":"真实结构化输出"}
```
"""

    payload = extract_json_object_from_text(mixed_output)

    assert payload["title"] == "联合索引导学"
    assert payload["summary"] == "真实结构化输出"


def test_extract_json_object_from_text_prefers_outermost_object_for_plain_json() -> None:
    mixed_output = """
{
  "title": "联合索引导学",
  "slides": [
    {
      "title": "第一页",
      "bullets": ["A", "B"]
    }
  ]
}
"""

    payload = extract_json_object_from_text(mixed_output)

    assert payload["title"] == "联合索引导学"
    assert isinstance(payload["slides"], list)


class _FakeStreamResponse:
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    def raise_for_status(self) -> None:
        return None

    async def aiter_lines(self):
        for line in self.lines:
            yield line


class _FakeAsyncClient:
    def __init__(self, lines: list[str]) -> None:
        self.lines = lines
        self.request_json = None
        self.request_headers = None

    def stream(self, method, url, *, headers, json):
        self.request_json = json
        self.request_headers = headers
        return _FakeStreamResponse(self.lines)


@pytest.mark.asyncio
async def test_openai_compatible_client_streams_delta_content(monkeypatch) -> None:
    fake_client = _FakeAsyncClient(
        [
            'data: {"choices":[{"delta":{"content":"Hel"}}]}',
            'data: {"choices":[{"delta":{"content":"lo"}}]}',
            'data: [DONE]',
        ]
    )
    client = OpenAICompatibleClient(
        api_key="test-key",
        base_url="https://llm.example.test/v1",
        model_name="test-model",
    )

    async def fake_get_client():
        return fake_client

    monkeypatch.setattr(client, "_get_client", fake_get_client)

    chunks = [
        chunk
        async for chunk in client.chat_completion_stream(
            messages=[{"role": "user", "content": "hello"}],
        )
    ]

    assert chunks == ["Hel", "lo"]
    assert fake_client.request_json["stream"] is True
    assert fake_client.request_headers["Accept"] == "text/event-stream"
