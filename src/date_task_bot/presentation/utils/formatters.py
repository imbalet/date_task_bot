from datetime import datetime
from zoneinfo import ZoneInfo

from babel.dates import format_datetime


class DateFormatter:
    def __init__(self, timezone: str = "UTC") -> None:
        self.timezone = timezone

    def set_timezone(self, timezone: str) -> None:
        self.timezone = timezone

    def _to_tz(self, date: datetime) -> datetime:
        return date.astimezone(ZoneInfo(self.timezone))

    def _format_date(self, date: datetime, format: str) -> str:
        return format_datetime(self._to_tz(date), format, locale="ru")

    def format_date_long(self, date: datetime) -> str:
        return self._format_date(date, "EEEE, d MMMM y 'г.' HH:mm")

    def format_date_short(self, date: datetime) -> str:
        return self._format_date(date, "EEE, d MMM y 'г.' HH:mm")
