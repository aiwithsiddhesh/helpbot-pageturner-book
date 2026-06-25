from __future__ import annotations

import time
import random
import anthropic


def _with_retry(fn, retries=3):
    for attempt in range(retries):
        try:
            return fn()
        except (anthropic.RateLimitError, anthropic.APIStatusError):
            if attempt == retries - 1:
                raise
            time.sleep((2 ** attempt) + random.random())
