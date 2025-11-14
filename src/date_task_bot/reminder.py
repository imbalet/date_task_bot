import asyncio
from logging import getLogger

from aiogram import Bot

from date_task_bot.presentation.services import Sender
from date_task_bot.presentation.utils import DateFormatter, ReminderFormatter
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

    async def worker(self):
        while True:
            reminder: DueReminder = await self.queue.get()

            try:
                formatter = ReminderFormatter(DateFormatter(reminder.timezone))
                await self.sender.send_message(
                    chat_id=int(reminder.user_id), text=formatter.format(reminder)
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

    async def reminder_loop(self):
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

    def start(self):
        self.workers = [
            asyncio.create_task(self.worker()) for _ in range(self.concurrent_sending)
        ]
        self.loop = asyncio.create_task(self.reminder_loop())
        logger.info("Reminder service started.")

    async def stop(self):
        if self.loop:
            self.loop.cancel()
            try:
                await self.loop
            except BaseException:
                pass
        for i in self.workers:
            i.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
        logger.info("Reminder service stopped.")
