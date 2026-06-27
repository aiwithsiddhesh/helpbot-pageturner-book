from __future__ import annotations

import time

_SESSION_TIMEOUT = 1800  # 30 minutes
_RATE_LIMIT = 5


class Session:
    def __init__(self) -> None:
        self.email: str | None = None
        self.verified: bool = False
        self.timestamp: float | None = None
        self.rate_counter: int = 0

    def set(self, email: str, verified: bool = False) -> None:
        self.email = email.lower().strip()
        self.verified = verified
        self.timestamp = time.time()
        self.rate_counter = 0

    def is_valid(self) -> bool:
        if not self.verified or self.email is None or self.timestamp is None:
            return False
        return (time.time() - self.timestamp) < _SESSION_TIMEOUT

    def expire(self) -> None:
        self.email = None
        self.verified = False
        self.timestamp = None

    def rate_limit_reached(self) -> bool:
        return self.rate_counter >= _RATE_LIMIT

    def increment_rate(self) -> None:
        self.rate_counter += 1
