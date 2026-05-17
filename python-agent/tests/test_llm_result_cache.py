import pytest

from src.ai_modules.llms.agent_models import OpenAICompatibleJSONGenerator
from src.ai_modules.llms.openai_compatible import extract_json_object_from_text


class FakeJSONClient:
    provider_name = "openai_compatible"
    model_name = "cache-test-model"

    def __init__(self) -> None:
        self.calls = 0

    async def chat_completion(self, **kwargs):
        del kwargs
        self.calls += 1
        return {
            "choices": [
                {
                    "message": {
                        "content": '{"value":"cached","items":[{"title":"stable"}]}'
                    }
                }
            ]
        }

    def extract_message(self, response_json):
        return response_json["choices"][0]["message"]

    def extract_content(self, message):
        return message["content"]

    def parse_json_text(self, content):
        return extract_json_object_from_text(content)


@pytest.mark.asyncio
async def test_json_generator_cache_returns_exact_deep_copied_payload() -> None:
    fake_client = FakeJSONClient()
    generator = OpenAICompatibleJSONGenerator(
        model_name="cache-test-model",
        cache_namespace="unit-test-json",
    )
    generator.client = fake_client

    first = await generator.generate(
        system_prompt="stable system",
        user_prompt="same user payload",
        max_tokens=64,
    )
    first["items"][0]["title"] = "mutated"
    second = await generator.generate(
        system_prompt="stable system",
        user_prompt="same user payload",
        max_tokens=64,
    )

    assert fake_client.calls == 1
    assert second["items"][0]["title"] == "stable"
