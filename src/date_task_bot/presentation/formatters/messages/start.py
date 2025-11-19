from date_task_bot.presentation.constants import TEXTS, MsgKey


class StartCommandMessageFormatter:

    def format(self, formatted_timezone: str):
        return (
            f"{TEXTS[MsgKey.WELCOME_MESSAGE]}.\n"
            + f"{TEXTS[MsgKey.CURRENT_TIMEZONE]}: {formatted_timezone}.\n{TEXTS[MsgKey.CHANGE_TIMEZONE]}"
        )
