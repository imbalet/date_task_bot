import asyncio
from functools import wraps
from logging import getLogger

from aiogram import Bot
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.types import Message

from .rate_limiter import RateLimiter

logger = getLogger(__name__)


class Sender:
    def __init__(self, bot: Bot, *, rate: int = 30, per: int = 1) -> None:
        self.rate_limiter = RateLimiter(rate=rate, per=per)
        self.bot = bot

    @staticmethod
    def error_handler(retries: int = 3):
        def error_handler_dec(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                attempt = 0
                while attempt <= retries:
                    try:
                        attempt += 1
                        return await func(*args, **kwargs)

                    except TelegramRetryAfter as e:
                        logger.warning("FLOOD_WAIT: waiting %d seconds.", e.retry_after)
                        await asyncio.sleep(e.retry_after)

                    except TelegramForbiddenError:
                        logger.warning("Bot was blocked by user.")

                    except TelegramBadRequest:
                        logger.error("Telegram bad request", exc_info=True)

                    except Exception:
                        logger.error("Unexpected send error", exc_info=True)
                return None

            return wrapper

        return error_handler_dec

    @error_handler()
    async def send_message(self, chat_id: int, text: str, **kwargs):
        await self.rate_limiter.acquire()
        await self.bot.send_message(chat_id=chat_id, text=text, **kwargs)

    @error_handler()
    async def answer_message(self, message: Message, text: str, **kwargs):
        await self.rate_limiter.acquire()
        await message.answer(text=text, **kwargs)
