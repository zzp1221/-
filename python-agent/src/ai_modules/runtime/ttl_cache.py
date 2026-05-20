"""Small in-process TTL cache for exact runtime results."""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from dataclasses import dataclass, field
import hashlib
import json
from threading import RLock
from time import monotonic
from typing import Any

from pydantic import BaseModel


def stable_cache_key(namespace: str, payload: Any) -> str:
    """Build a stable key from JSON-compatible payload content."""

    normalized_payload = _normalize_for_cache(payload)
    encoded = json.dumps(
        normalized_payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    digest = hashlib.sha256(encoded).hexdigest()
    return f"{namespace}:{digest}"


@dataclass(slots=True)
class AdaptiveCacheStats:
    """Lightweight namespace-local cache effectiveness counters."""

    window_size: int
    outcomes: deque[bool] = field(default_factory=deque)
    hits: int = 0
    misses: int = 0
    sets: int = 0
    bypasses: int = 0
    probes: int = 0
    skipped_large_values: int = 0
    bypass_until: float = 0.0
    bypass_counter: int = 0

    def resize(self, window_size: int) -> None:
        self.window_size = max(1, window_size)
        while len(self.outcomes) > self.window_size:
            self.outcomes.popleft()

    @property
    def samples(self) -> int:
        return len(self.outcomes)

    @property
    def hit_rate(self) -> float:
        if not self.outcomes:
            return 0.0
        return sum(1 for item in self.outcomes if item) / len(self.outcomes)

    def record_outcome(self, hit: bool) -> None:
        if len(self.outcomes) >= self.window_size:
            self.outcomes.popleft()
        self.outcomes.append(hit)
        if hit:
            self.hits += 1
        else:
            self.misses += 1


class InMemoryTTLCache:
    """Thread-safe bounded TTL cache with adaptive namespace bypass."""

    def __init__(
        self,
        *,
        max_entries: int = 256,
        adaptive_enabled: bool = True,
        adaptive_window_size: int = 100,
        adaptive_min_samples: int = 50,
        adaptive_min_hit_rate: float = 0.10,
        adaptive_bypass_seconds: int = 60,
        adaptive_probe_interval: int = 20,
        max_value_bytes: int = 262144,
    ) -> None:
        self.max_entries = max(1, max_entries)
        self._items: dict[str, tuple[float, float, Any]] = {}
        self._stats: dict[str, AdaptiveCacheStats] = {}
        self._lock = RLock()
        self.configure(
            adaptive_enabled=adaptive_enabled,
            adaptive_window_size=adaptive_window_size,
            adaptive_min_samples=adaptive_min_samples,
            adaptive_min_hit_rate=adaptive_min_hit_rate,
            adaptive_bypass_seconds=adaptive_bypass_seconds,
            adaptive_probe_interval=adaptive_probe_interval,
            max_value_bytes=max_value_bytes,
        )

    def configure(
        self,
        *,
        adaptive_enabled: bool | None = None,
        adaptive_window_size: int | None = None,
        adaptive_min_samples: int | None = None,
        adaptive_min_hit_rate: float | None = None,
        adaptive_bypass_seconds: int | None = None,
        adaptive_probe_interval: int | None = None,
        max_value_bytes: int | None = None,
    ) -> None:
        with self._lock:
            if adaptive_enabled is not None:
                self.adaptive_enabled = adaptive_enabled
            if adaptive_window_size is not None:
                self.adaptive_window_size = max(1, adaptive_window_size)
                for stats in self._stats.values():
                    stats.resize(self.adaptive_window_size)
            if adaptive_min_samples is not None:
                self.adaptive_min_samples = max(1, adaptive_min_samples)
            if adaptive_min_hit_rate is not None:
                self.adaptive_min_hit_rate = min(1.0, max(0.0, adaptive_min_hit_rate))
            if adaptive_bypass_seconds is not None:
                self.adaptive_bypass_seconds = max(0, adaptive_bypass_seconds)
            if adaptive_probe_interval is not None:
                self.adaptive_probe_interval = max(1, adaptive_probe_interval)
            if max_value_bytes is not None:
                self.max_value_bytes = max(0, max_value_bytes)

    def should_read(self, namespace: str) -> bool:
        """Return whether callers should build a key and try the cache."""

        if not self.adaptive_enabled:
            return True
        now = monotonic()
        with self._lock:
            stats = self._stats_for(namespace)
            if stats.bypass_until <= now:
                return True

            stats.bypasses += 1
            stats.bypass_counter += 1
            if stats.bypass_counter % self.adaptive_probe_interval == 0:
                stats.probes += 1
                return True
            return False

    def get(self, key: str, *, namespace: str | None = None) -> Any | None:
        namespace = namespace or self._namespace_from_key(key)
        now = monotonic()
        with self._lock:
            item = self._items.get(key)
            if item is None:
                self._record_outcome(namespace, hit=False, now=now)
                return None
            expires_at, created_at, value = item
            if expires_at <= now:
                self._items.pop(key, None)
                self._record_outcome(namespace, hit=False, now=now)
                return None
            self._items[key] = (expires_at, created_at, value)
            self._record_outcome(namespace, hit=True, now=now)
            return deepcopy(value)

    def set(
        self,
        key: str,
        value: Any,
        *,
        ttl_seconds: int,
        namespace: str | None = None,
    ) -> None:
        if ttl_seconds <= 0:
            return
        namespace = namespace or self._namespace_from_key(key)
        now = monotonic()
        with self._lock:
            stats = self._stats_for(namespace)
            if self.adaptive_enabled and stats.bypass_until > now:
                return
            if not self._value_fits(value, namespace):
                return
            self._items[key] = (now + ttl_seconds, now, deepcopy(value))
            stats.sets += 1
            self._evict_if_needed(now)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()
            self._stats.clear()

    def namespace_stats(self, namespace: str) -> dict[str, Any]:
        with self._lock:
            stats = self._stats_for(namespace)
            return {
                "samples": stats.samples,
                "hitRate": stats.hit_rate,
                "hits": stats.hits,
                "misses": stats.misses,
                "sets": stats.sets,
                "bypasses": stats.bypasses,
                "probes": stats.probes,
                "skippedLargeValues": stats.skipped_large_values,
                "isBypassed": stats.bypass_until > monotonic(),
            }

    def _evict_if_needed(self, now: float) -> None:
        expired_keys = [
            key
            for key, (expires_at, _, _) in self._items.items()
            if expires_at <= now
        ]
        for key in expired_keys:
            self._items.pop(key, None)

        overflow = len(self._items) - self.max_entries
        if overflow <= 0:
            return
        oldest_keys = sorted(
            self._items,
            key=lambda key: self._items[key][1],
        )[:overflow]
        for key in oldest_keys:
            self._items.pop(key, None)

    def _stats_for(self, namespace: str) -> AdaptiveCacheStats:
        stats = self._stats.get(namespace)
        if stats is None:
            stats = AdaptiveCacheStats(window_size=self.adaptive_window_size)
            self._stats[namespace] = stats
        return stats

    def _record_outcome(self, namespace: str, *, hit: bool, now: float) -> None:
        if not self.adaptive_enabled:
            return
        stats = self._stats_for(namespace)
        stats.record_outcome(hit)
        if hit and stats.hit_rate >= self.adaptive_min_hit_rate:
            stats.bypass_until = 0.0
            stats.bypass_counter = 0
            return
        if stats.samples < self.adaptive_min_samples:
            return
        if stats.hit_rate < self.adaptive_min_hit_rate:
            stats.bypass_until = now + self.adaptive_bypass_seconds
            stats.bypass_counter = 0

    def _value_fits(self, value: Any, namespace: str) -> bool:
        if self.max_value_bytes <= 0:
            return True
        try:
            normalized = _normalize_for_cache(value)
            encoded = json.dumps(
                normalized,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        except (TypeError, ValueError):
            self._stats_for(namespace).skipped_large_values += 1
            return False
        if len(encoded) > self.max_value_bytes:
            self._stats_for(namespace).skipped_large_values += 1
            return False
        return True

    def _namespace_from_key(self, key: str) -> str:
        namespace, _, _ = key.partition(":")
        return namespace or "default"


def _normalize_for_cache(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return _normalize_for_cache(value.model_dump(by_alias=True))
    if isinstance(value, dict):
        return {
            str(key): _normalize_for_cache(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [_normalize_for_cache(item) for item in value]
    if isinstance(value, set):
        return sorted(_normalize_for_cache(item) for item in value)
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    return str(value)
