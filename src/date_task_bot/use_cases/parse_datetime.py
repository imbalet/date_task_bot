from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from dateparser.search import search_dates


@dataclass
class ParseDateTimeUseCaseResult:
    """
    success (bool): False if there is no datetime in the text.\n
    date (datetime): Parsed datetime in the UTC time zone from text.\n
    text (str): The text without datetime.
    """

    success: bool = True
    date: datetime | None = None
    text: str | None = None


class ParseDateTimeUseCase:
    def execute(self, user_tz_str: str, text: str) -> ParseDateTimeUseCaseResult:
        """Parses datetime from text.

        Args:
            user_tz_str (str): Timezone in IANA format.
            text (str): text with datetime.

        Returns:
            ParseDateTimeUseCaseResult: Result schema. Date will be presented in the UTC time zone.
        """
        user_tz = ZoneInfo(user_tz_str)
        settings = {
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.now(user_tz).replace(tzinfo=None),
            "DEFAULT_LANGUAGES": ["ru"],
            "TIMEZONE": user_tz_str,
            "RETURN_AS_TIMEZONE_AWARE": True,
        }

        dates = search_dates(text, languages=["ru"], settings=settings)
        if not dates:
            return ParseDateTimeUseCaseResult(success=False)

        # find a date substring with maximum length
        date_text, date = max(dates, key=lambda x: len(x[0]))
        text = text.replace(date_text, "").strip()

        return ParseDateTimeUseCaseResult(date=date.astimezone(UTC), text=text)
