from .datetime_formatter import DateFormatter


class BaseFormatterWithDate:
    def __init__(self, user_tz: str) -> None:
        self.date_formatter = DateFormatter(user_tz)
