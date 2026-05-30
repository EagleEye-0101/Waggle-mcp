import pytest

from waggle.rate_limit import RateLimiter


@pytest.mark.anyio
async def test_concurrency_key_removed_when_count_reaches_zero():
    limiter = RateLimiter(
        requests_per_minute=10,
        max_concurrent_requests=2,
    )

    async with limiter.concurrency_slot("user1"):
        assert "user1" in limiter._concurrent

    assert "user1" not in limiter._concurrent
