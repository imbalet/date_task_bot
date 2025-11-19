from date_task_bot.presentation.constants import TEXTS, MsgKey


class AllTasksMessageFormatter:
    def format(self, formatted_task_list: str):
        return f"{TEXTS[MsgKey.YOUR_TASKS]}:\n{formatted_task_list}"
