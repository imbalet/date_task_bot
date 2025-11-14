import asyncio
import time


class RateLimiter:
    def __init__(self, rate: int, per: float):
        self.rate = rate  # message count
        self.per = per  # send timings in seconds
        self.tokens = rate
        self.updated = time.time()
        self.lock = asyncio.Lock()

    async def acquire(self):
        async with self.lock:
            now = time.time()
            delta = now - self.updated
            self.updated = now

            self.tokens = min(self.rate, self.tokens + delta * (self.rate / self.per))

            if self.tokens < 1:
                wait = (1 - self.tokens) * (self.per / self.rate)
                await asyncio.sleep(wait)
                self.tokens = 0

            self.tokens -= 1
