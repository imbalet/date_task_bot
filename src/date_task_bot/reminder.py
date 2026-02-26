import asyncio
import contextlib
from logging import getLogger

from aiogram import Bot

from date_task_bot.presentation.formatters.models import DueReminderFormatter
from date_task_bot.presentation.services import Sender
from date_task_bot.repositories import ReminderRepository
from date_task_bot.repositories.schemas import DueReminder
from date_task_bot.schemas import ReminderStatus

logger = getLogger(__name__)


class Reminder:
    def __init__(
        self,
        bot: Bot,
        sender: Sender,
        reminder_repo: ReminderRepository,
        *,
        sleep_time_seconds: int = 30,
        concurrent_sending: int = 10,
    ) -> None:
        self.bot = bot
        self.reminder_repo = reminder_repo
        self.sleep_time_seconds = sleep_time_seconds
        self.concurrent_sending = concurrent_sending
        self.sender = sender

        self.queue = asyncio.Queue()
        self.workers = []
        self.loop = None

    async def worker(self) -> None:
        while True:
            reminder: DueReminder = await self.queue.get()

            try:
                formatter = DueReminderFormatter(reminder.timezone)
                await self.sender.send_message(
                    user_id=int(reminder.user_id), text=formatter.format(reminder)
                )
            except Exception:
                await self.reminder_repo.set_status(reminder.id, ReminderStatus.FAILED)
                logger.warning(
                    "Error on sending reminder for task with id %s.",
                    reminder.id,
                    exc_info=True,
                )
                pass
            else:
                await self.reminder_repo.set_status(reminder.id, ReminderStatus.SENT)

            self.queue.task_done()

    async def reminder_loop(self) -> None:
        while 1:
            try:
                due_reminders = await self.reminder_repo.reserve_due_reminders()
                logger.debug("Got %d reminders from db", len(due_reminders))
                for i in due_reminders:
                    await self.queue.put(i)
                await asyncio.sleep(self.sleep_time_seconds)
            except asyncio.CancelledError:
                logger.info("Reminder loop was cancelled.")
                break

            except BaseException:
                logger.critical("Reminder loop stopped unexpectedly.", exc_info=True)
                pass

    async def start(self) -> None:
        self.workers = [
            asyncio.create_task(self.worker()) for _ in range(self.concurrent_sending)
        ]
        await self.reminder_repo.recover_stuck_reminders()
        self.loop = asyncio.create_task(self.reminder_loop())
        logger.info("Reminder service started.")

    async def stop(self) -> None:
        if self.loop:
            self.loop.cancel()
            with contextlib.suppress(BaseException):
                await self.loop
        for i in self.workers:
            i.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info("Reminder service stopped.")
