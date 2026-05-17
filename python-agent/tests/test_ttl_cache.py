from time import sleep

from src.ai_modules.runtime import InMemoryTTLCache, stable_cache_key


def test_in_memory_ttl_cache_returns_deep_copies() -> None:
    cache = InMemoryTTLCache(max_entries=4)
    key = stable_cache_key("unit", {"query": "java", "keywords": ["thread"]})

    cache.set(key, {"items": [{"title": "thread"}]}, ttl_seconds=30)
    first = cache.get(key)
    first["items"][0]["title"] = "mutated"

    second = cache.get(key)

    assert second == {"items": [{"title": "thread"}]}


def test_in_memory_ttl_cache_expires_entries() -> None:
    cache = InMemoryTTLCache(max_entries=4)
    key = stable_cache_key("unit", {"query": "ttl"})

    cache.set(key, {"ok": True}, ttl_seconds=1)
    sleep(1.1)

    assert cache.get(key) is None
