"""Key pool — multi-key rotation with health tracking."""

from __future__ import annotations

import itertools
import time
from collections.abc import Iterator
from dataclasses import dataclass, field


@dataclass
class KeyState:
    key: str
    errors: int = 0
    cooldown_until: float = 0.0
    total_uses: int = 0

    @property
    def is_available(self) -> bool:
        return self.cooldown_until < time.time()

    def record_error(self) -> None:
        self.errors += 1
        # Exponential backoff: 5s, 10s, 20s, 40s, max 120s
        backoff = min(5 * (2 ** (self.errors - 1)), 120)
        self.cooldown_until = time.time() + backoff

    def record_success(self) -> None:
        self.total_uses += 1
        # Reset error count on success (graceful recovery)
        if self.errors > 0:
            self.errors = max(0, self.errors - 1)


class KeyPool:
    """Rotate through multiple API keys with health tracking.

    Supports round-robin rotation. Keys that error out get a temporary
    cooldown before being retried. If all keys are in cooldown, the least-
    recently-failed key is used as a fallback.

    Usage:
        pool = KeyPool(["key1", "key2", "key3"])
        key = pool.next()
        # ... use key ...
        pool.record_success(key)  # or record_error(key)
    """

    def __init__(self, keys: list[str]) -> None:
        self._keys = [KeyState(k) for k in keys if k]
        self._cycle: Iterator[KeyState] | None = None

    @property
    def total_keys(self) -> int:
        return len(self._keys)

    @property
    def available_keys(self) -> int:
        return sum(1 for k in self._keys if k.is_available)

    @property
    def all_keys(self) -> list[str]:
        return [k.key for k in self._keys]

    def next(self) -> str | None:
        """Get the next available key, or the best-effort fallback."""
        if not self._keys:
            return None

        # Ensure cycle exists
        if self._cycle is None:
            self._cycle = itertools.cycle(self._keys)

        # Try up to total_keys times to find an available key
        cycle = self._cycle
        for _ in range(len(self._keys)):
            candidate = next(cycle)
            if candidate.is_available:
                return candidate.key

        # All keys on cooldown — pick the one with the shortest remaining cooldown
        fallback = min(self._keys, key=lambda k: k.cooldown_until)
        return fallback.key

    def record_success(self, key: str) -> None:
        for state in self._keys:
            if state.key == key:
                state.record_success()
                return

    def record_error(self, key: str) -> None:
        for state in self._keys:
            if state.key == key:
                state.record_error()
                return

    def health(self) -> list[dict]:
        """Return key health status for admin UI."""
        now = time.time()
        return [
            {
                "key": _mask_key(k.key),
                "available": k.is_available,
                "errors": k.errors,
                "uses": k.total_uses,
                "cooldown_remaining": max(0, round(k.cooldown_until - now, 1)),
            }
            for k in self._keys
        ]


def _mask_key(key: str) -> str:
    """Mask API key for display — show first 8 + last 4 chars."""
    if len(key) < 16:
        return key[:6] + "..." if len(key) > 6 else key
    return key[:8] + "..." + key[-4:]
