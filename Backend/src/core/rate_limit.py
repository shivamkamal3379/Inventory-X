"""A small in-process fixed-window rate limiter for the login endpoint.

Deliberately dependency-free and per-process: with the default single-container
deployment that is exactly one counter. If you scale the API to several replicas,
move this to Redis — each replica would otherwise keep its own count and the
effective limit multiplies by the replica count. See docs/DEPLOYMENT.md.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from src.core.config import settings


class SlidingWindowLimiter:
    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str) -> tuple[bool, int]:
        """Record a hit for `key`. Returns (allowed, seconds_until_retry)."""
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] < cutoff:
                hits.popleft()

            if len(hits) >= self.max_attempts:
                retry_after = int(hits[0] + self.window_seconds - now) + 1
                return False, retry_after

            hits.append(now)

            # Opportunistic cleanup so idle keys don't accumulate forever.
            if len(self._hits) > 10_000:
                for k in [k for k, v in self._hits.items() if not v]:
                    del self._hits[k]
            return True, 0

    def reset(self, key: str) -> None:
        with self._lock:
            self._hits.pop(key, None)


login_limiter = SlidingWindowLimiter(
    max_attempts=settings.LOGIN_RATE_LIMIT_ATTEMPTS,
    window_seconds=settings.LOGIN_RATE_LIMIT_WINDOW_SECONDS,
)


def client_key(request: Request) -> str:
    """Identify the caller for rate-limiting.

    X-Forwarded-For is only trusted because the documented deployment always puts
    nginx in front of the API and nginx overwrites the header. Exposing this
    container directly to the internet would let a client spoof its own key.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def enforce_login_rate_limit(request: Request) -> None:
    allowed, retry_after = login_limiter.check(client_key(request))
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
            headers={"Retry-After": str(retry_after)},
        )
