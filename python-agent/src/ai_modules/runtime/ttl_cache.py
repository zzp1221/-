"""Small in-process TTL cache for exact, read-through runtime results."""

from __future__ import annotations

from copy import deepcopy
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


class InMemoryTTLCache:
    """Thread-safe bounded TTL cache that never returns mutable internals."""

    def __init__(self, *, max_entries: int = 256) -> None:
        self.max_entries = max(1, max_entries)
        self._items: dict[str, tuple[float, float, Any]] = {}
        self._lock = RLock()

    def get(self, key: str) -> Any | None:
        now = monotonic()
        with self._lock:
            item = self._items.get(key)
            if item is None:
                return None
            expires_at, created_at, value = item
            if expires_at <= now:
                self._items.pop(key, None)
                return None
            self._items[key] = (expires_at, created_at, value)
            return deepcopy(value)

    def set(self, key: str, value: Any, *, ttl_seconds: int) -> None:
        if ttl_seconds <= 0:
            return
        now = monotonic()
        with self._lock:
            self._items[key] = (now + ttl_seconds, now, deepcopy(value))
            self._evict_if_needed(now)

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

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
