from date_task_bot.presentation.constants import TEXTS, MsgKey


class CreatedTaskMessageFormatter:

    def format(self, formatted_task: str):
        return f"{TEXTS[MsgKey.CREATED_TASK]}:\n{formatted_task}"
