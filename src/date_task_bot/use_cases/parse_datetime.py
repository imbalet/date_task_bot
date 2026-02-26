from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from zoneinfo import ZoneInfo

from dateparser.search import search_dates


@dataclass
class ParseDateTimeUseCaseResult:
    """Result of executing ParseDateTimeUseCase.

    Fields:
        success (bool): False if there is no datetime in the text.
        date (datetime): Parsed datetime in the UTC time zone from text.
        text (str): The text without datetime.
    """

    success: bool = True
    date: datetime | None = None
    text: str | None = None


class ParseDateTimeUseCase:
    def __init__(self) -> None:
        self.languages = ["ru"]

    def execute(
        self, user_tz_str: str, text: str, now: datetime | None = None
    ) -> ParseDateTimeUseCaseResult:
        """Parses datetime from text.

        Args:
            user_tz_str (str): Timezone in IANA format.
            text (str): Text with datetime.
            now (datetime | None, optional): Base datetime. Uses now() if not passed.
                Defaults to None.

        Returns:
            ParseDateTimeUseCaseResult: Parsing result.
        """
        user_tz = ZoneInfo(user_tz_str)
        base_datetime = now or datetime.now(user_tz).replace(tzinfo=None)
        settings = self._build_settings(relative_base=base_datetime)

        is_only_time = self._is_only_time(text=text)
        if is_only_time:
            settings = {**settings, "PREFER_DATES_FROM": "current_period"}

        res = self._parse(text=text, settings=settings)
        if not res:
            return ParseDateTimeUseCaseResult(success=False)
        date_text, date = res
        if is_only_time and date < base_datetime:
            date += timedelta(days=1)

        cleaned_text = text.replace(date_text, "").strip()

        return ParseDateTimeUseCaseResult(
            date=date.replace(tzinfo=user_tz).astimezone(UTC), text=cleaned_text
        )

    def _parse(self, text: str, settings: dict) -> tuple[str, datetime] | None:
        dates = search_dates(text, languages=self.languages, settings=settings)
        if not dates:
            return None

        date_text, date = max(dates, key=lambda x: len(x[0]))
        return date_text, date

    def _is_only_time(self, text: str) -> bool:
        """Returns True if only time is present in the text.

        Parses text twice with different base dates.
        If the date parts of results match base dates,
        only time is present in the text and True is returned, otherwise False

        Args:
            text (str): Text to parse.

        Returns:
            bool: True if only time is present in the text, False otherwise.
        """
        sandbox_settings = {
            "TIMEZONE": "UTC",
            "RETURN_AS_TIMEZONE_AWARE": False,
            "DEFAULT_LANGUAGES": self.languages,
        }

        base1 = datetime(2020, 1, 15, 0, 0)
        base2 = datetime(2021, 6, 20, 0, 0)

        res1 = self._parse(text, settings={**sandbox_settings, "RELATIVE_BASE": base1})
        res2 = self._parse(text, settings={**sandbox_settings, "RELATIVE_BASE": base2})
        if not res1 or not res2:
            return False

        _, dt1 = res1
        _, dt2 = res2

        return bool(dt1.date() == base1.date() and dt2.date() == base2.date())

    def _build_settings(self, relative_base: datetime) -> dict:
        return {
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": relative_base,
            "DEFAULT_LANGUAGES": self.languages,
            "TIMEZONE": "UTC",
            "RETURN_AS_TIMEZONE_AWARE": False,
        }
