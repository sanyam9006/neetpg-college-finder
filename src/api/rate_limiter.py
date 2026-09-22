import os
import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class BaseRateLimiter(ABC):
    """Abstract Base Class for Rate Limiters."""

    @abstractmethod
    def is_allowed(self, key: str, limit: int = 10, window_seconds: int = 60) -> bool:
        """Determines if a request for `key` is within the rate limit window."""
        pass


class InMemoryRateLimiter(BaseRateLimiter):
    """
    Thread-safe in-memory sliding-window rate limiter for local development
    and single-worker deployments.
    """

    def __init__(self):
        self._store: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def is_allowed(self, key: str, limit: int = 10, window_seconds: int = 60) -> bool:
        now = time.time()
        with self._lock:
            timestamps = self._store.get(key, [])
            # Filter timestamps outside the sliding window
            timestamps = [t for t in timestamps if now - t < window_seconds]
            if len(timestamps) >= limit:
                self._store[key] = timestamps
                return False
            timestamps.append(now)
            self._store[key] = timestamps
            return True


class RedisRateLimiter(BaseRateLimiter):
    """
    Distributed sliding-window rate limiter powered by Redis.
    Safe for horizontal scaling across multiple container replicas/workers.
    """

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self._client = None
        self._fallback = InMemoryRateLimiter()

        try:
            import redis
            self._client = redis.from_url(redis_url, decode_responses=True, socket_timeout=2.0)
            self._client.ping()
        except Exception as e:
            print(f"Warning: Could not connect to Redis ({e}). Falling back to InMemoryRateLimiter.")
            self._client = None

    def is_allowed(self, key: str, limit: int = 10, window_seconds: int = 60) -> bool:
        if not self._client:
            return self._fallback.is_allowed(key, limit, window_seconds)

        now = time.time()
        redis_key = f"ratelimit:{key}"
        clear_before = now - window_seconds

        try:
            pipe = self._client.pipeline()
            # Remove old requests
            pipe.zremrangebyscore(redis_key, 0, clear_before)
            # Count remaining requests
            pipe.zcard(redis_key)
            # Add current timestamp
            pipe.zadd(redis_key, {str(now): now})
            # Set TTL to expire automatically
            pipe.expire(redis_key, window_seconds + 5)
            results = pipe.execute()

            current_count = results[1]
            if current_count >= limit:
                return False
            return True
        except Exception as e:
            print(f"Redis rate limiter exception ({e}), using in-memory fallback.")
            return self._fallback.is_allowed(key, limit, window_seconds)


_rate_limiter_instance: Optional[BaseRateLimiter] = None


def get_rate_limiter() -> BaseRateLimiter:
    """
    Returns the configured rate limiter singleton.
    Uses Redis when REDIS_URL environment variable is provided, else in-memory.
    """
    global _rate_limiter_instance
    if _rate_limiter_instance is None:
        redis_url = os.environ.get("REDIS_URL")
        if redis_url:
            _rate_limiter_instance = RedisRateLimiter(redis_url)
        else:
            _rate_limiter_instance = InMemoryRateLimiter()
    return _rate_limiter_instance
