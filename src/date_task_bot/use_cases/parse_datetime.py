from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo

from dateparser.search import search_dates


@dataclass
class ParseDateTimeUseCaseResult:
    success: bool = True
    date: datetime | None = None
    text: str | None = None


class ParseDateTimeUseCase:
    def execute(self, user_tz: str, text: str) -> ParseDateTimeUseCaseResult:
        settings = {
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": datetime.now(ZoneInfo(user_tz)),
            "DEFAULT_LANGUAGES": ["ru"],
            "TIMEZONE": user_tz,
            "RETURN_AS_TIMEZONE_AWARE": True,
        }

        dates = search_dates(text, languages=["ru"], settings=settings)
        if not dates:
            return ParseDateTimeUseCaseResult(success=False)

        # find a date substring with maximum length
        date = max(dates, key=lambda x: len(x[0]))
        text = text.replace(date[0], "")

        return ParseDateTimeUseCaseResult(date=date[1], text=text)
