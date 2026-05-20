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


def test_adaptive_cache_bypasses_after_low_hit_rate() -> None:
    cache = InMemoryTTLCache(
        max_entries=4,
        adaptive_window_size=3,
        adaptive_min_samples=3,
        adaptive_min_hit_rate=0.5,
        adaptive_bypass_seconds=60,
        adaptive_probe_interval=2,
    )

    for index in range(3):
        assert cache.get(f"low-hit:{index}", namespace="low-hit") is None

    stats = cache.namespace_stats("low-hit")
    assert stats["isBypassed"] is True
    assert cache.should_read("low-hit") is False
    assert cache.should_read("low-hit") is True
    assert cache.namespace_stats("low-hit")["probes"] == 1


def test_adaptive_cache_skips_writes_while_bypassed() -> None:
    cache = InMemoryTTLCache(
        max_entries=4,
        adaptive_window_size=2,
        adaptive_min_samples=2,
        adaptive_min_hit_rate=0.5,
        adaptive_bypass_seconds=60,
    )
    assert cache.get("write-bypass:missing-a", namespace="write-bypass") is None
    assert cache.get("write-bypass:missing-b", namespace="write-bypass") is None

    key = stable_cache_key("write-bypass", {"query": "late"})
    cache.set(key, {"ok": True}, ttl_seconds=30, namespace="write-bypass")

    assert cache.namespace_stats("write-bypass")["sets"] == 0


def test_adaptive_cache_keeps_high_hit_namespace_enabled() -> None:
    cache = InMemoryTTLCache(
        max_entries=4,
        adaptive_window_size=4,
        adaptive_min_samples=2,
        adaptive_min_hit_rate=0.5,
    )
    key = stable_cache_key("high-hit", {"query": "repeat"})
    cache.set(key, {"ok": True}, ttl_seconds=30, namespace="high-hit")

    assert cache.get(key, namespace="high-hit") == {"ok": True}
    assert cache.get(key, namespace="high-hit") == {"ok": True}

    stats = cache.namespace_stats("high-hit")
    assert stats["isBypassed"] is False
    assert stats["hitRate"] == 1.0
    assert cache.should_read("high-hit") is True


def test_adaptive_cache_probe_can_restore_bypassed_namespace() -> None:
    cache = InMemoryTTLCache(
        max_entries=4,
        adaptive_window_size=4,
        adaptive_min_samples=2,
        adaptive_min_hit_rate=0.5,
        adaptive_bypass_seconds=60,
        adaptive_probe_interval=1,
    )
    key = stable_cache_key("probe", {"query": "repeat"})
    cache.set(key, {"ok": True}, ttl_seconds=30, namespace="probe")
    assert cache.get("probe:missing-a", namespace="probe") is None
    assert cache.get("probe:missing-b", namespace="probe") is None
    assert cache.namespace_stats("probe")["isBypassed"] is True

    assert cache.should_read("probe") is True
    assert cache.get(key, namespace="probe") == {"ok": True}
    assert cache.should_read("probe") is True
    assert cache.get(key, namespace="probe") == {"ok": True}

    assert cache.namespace_stats("probe")["isBypassed"] is False


def test_adaptive_cache_skips_large_values() -> None:
    cache = InMemoryTTLCache(max_entries=4, max_value_bytes=16)
    key = stable_cache_key("large", {"query": "large"})

    cache.set(key, {"payload": "x" * 128}, ttl_seconds=30, namespace="large")

    assert cache.get(key, namespace="large") is None
    stats = cache.namespace_stats("large")
    assert stats["sets"] == 0
    assert stats["skippedLargeValues"] == 1
