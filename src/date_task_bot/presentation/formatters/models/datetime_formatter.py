from datetime import datetime, timedelta
from enum import StrEnum
from zoneinfo import ZoneInfo

from babel.dates import format_datetime, format_timedelta


class DateFormat(StrEnum):
    SHORT = "EEE, d MMM y 'г.' HH:mm"
    SHORT_NO_YEAR = "EEE, d MMM HH:mm"


class DateFormatter:
    def __init__(self, timezone: str = "UTC") -> None:
        self.timezone = timezone

    def _date_to_tz(self, date: datetime) -> datetime:
        return date.astimezone(ZoneInfo(self.timezone))

    def _format_date(self, date: datetime, format: str) -> str:
        return format_datetime(self._date_to_tz(date), format, locale="ru")

    def format(self, date: datetime, fmt: DateFormat) -> str:
        return self._format_date(date, fmt.value)


class TimeDeltaFormatter:
    def format(self, delta: timedelta):
        if abs(delta.total_seconds()) < 60:
            return ""
        return format_timedelta(
            delta, locale="ru", granularity="minute", threshold=1, format="short"
        )
