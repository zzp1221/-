from src.ai_modules.config import get_settings
from src.ai_modules.llms.mimo_client import MiMoClient


def test_mimo_client_uses_token_plan_base_url_for_tp_keys(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("MIMO_API_KEY", "tp-test-key")
    monkeypatch.setenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
    monkeypatch.setenv("OPENAI_COMPATIBLE_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

    client = MiMoClient()

    assert client.base_url == "https://token-plan-cn.xiaomimimo.com/v1"
    assert client._headers()["Authorization"] == "Bearer tp-test-key"

    get_settings.cache_clear()


def test_mimo_client_uses_configured_public_base_url_for_regular_keys(monkeypatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("MIMO_API_KEY", "sk-test-key")
    monkeypatch.setenv("MIMO_BASE_URL", "https://api.xiaomimimo.com/v1")
    monkeypatch.setenv("OPENAI_COMPATIBLE_BASE_URL", "https://token-plan-cn.xiaomimimo.com/v1")

    client = MiMoClient()

    assert client.base_url == "https://api.xiaomimimo.com/v1"
    assert client._headers()["Authorization"] == "Bearer sk-test-key"

    get_settings.cache_clear()
