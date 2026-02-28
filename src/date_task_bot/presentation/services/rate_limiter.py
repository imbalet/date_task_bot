import asyncio
import math
import time


class RateLimiter:
    def __init__(self, rate: int, per: float) -> None:
        self.rate = rate  # message count
        self.per = per  # send timings in seconds
        self.tokens: float = rate
        self.updated = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self) -> None:
        async with self.lock:
            now = time.time()
            delta = now - self.updated
            self.updated = now

            self.tokens = min(self.rate, self.tokens + delta * (self.rate / self.per))

            if self.tokens < 1:
                wait = (1 - self.tokens) * (self.per / self.rate)
                await asyncio.sleep(wait)
                self.tokens = 0

            self.tokens = math.floor(self.tokens)

            self.tokens -= 1
