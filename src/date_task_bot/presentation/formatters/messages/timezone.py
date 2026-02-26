from date_task_bot.presentation.constants import TEXTS, MsgKey


class TimezoneCommandMessageFormatter:
    def format(self, timezone: str, time: str) -> str:
        return f"""\
{TEXTS[MsgKey.SELECT_TIMEZONE]}. \
{TEXTS[MsgKey.CURRENT_TIMEZONE]}: {timezone}. \
{TEXTS[MsgKey.CURRENT_TIME]}: {time}"""


class TimezoneSetMessageFormatter:
    def format(self, timezone: str, time: str) -> str:
        return f"""\
{TEXTS[MsgKey.TIMEZONE_WAS_SET]}: {timezone}
{TEXTS[MsgKey.CURRENT_TIME]}: {time}"""
