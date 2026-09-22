import time
import pytest
from src.api.rate_limiter import InMemoryRateLimiter, get_rate_limiter


def test_in_memory_rate_limiter_allows_under_limit():
    limiter = InMemoryRateLimiter()
    key = "test_client_1"

    # 3 requests within limit of 3
    for _ in range(3):
        assert limiter.is_allowed(key, limit=3, window_seconds=2) is True


def test_in_memory_rate_limiter_blocks_over_limit():
    limiter = InMemoryRateLimiter()
    key = "test_client_2"

    for _ in range(3):
        assert limiter.is_allowed(key, limit=3, window_seconds=2) is True

    # 4th request should be blocked
    assert limiter.is_allowed(key, limit=3, window_seconds=2) is False


def test_in_memory_rate_limiter_resets_after_window():
    limiter = InMemoryRateLimiter()
    key = "test_client_3"

    # Fill window with 2 requests (short 0.2s window)
    assert limiter.is_allowed(key, limit=2, window_seconds=0.2) is True
    assert limiter.is_allowed(key, limit=2, window_seconds=0.2) is True
    assert limiter.is_allowed(key, limit=2, window_seconds=0.2) is False

    # Wait for window to expire
    time.sleep(0.25)

    # Should be allowed again
    assert limiter.is_allowed(key, limit=2, window_seconds=0.2) is True


def test_get_rate_limiter_factory():
    limiter = get_rate_limiter()
    assert limiter is not None
    assert hasattr(limiter, "is_allowed")
