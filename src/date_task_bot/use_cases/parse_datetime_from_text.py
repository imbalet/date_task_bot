from datetime import UTC, datetime
from typing import Iterable
from zoneinfo import ZoneInfo


class ParseDatetimeFromTextUseCase:

    DEFAULT_FORMATS: tuple[str, ...] = (
        "%d.%m.%y %H:%M",  # 13.01.26 15:45
        "%d.%m.%Y %H:%M",  # 13.01.2026 15:45
        "%Y-%m-%d %H:%M:%S",  # 2026-01-13 15:45:00
        "%Y-%m-%d %H:%M",  # 2026-01-13 15:45
        "%d/%m/%y %H:%M",  # 13/01/26 15:45
        "%d/%m/%Y %H:%M",  # 13/01/2026 15:45
        "%Y.%m.%d %H:%M:%S",  # 2026.01.13 15:45:00
        #
        "%d.%m.%y %H.%M",  # 13.01.26 15.45
        "%d.%m.%Y %H.%M",  # 13.01.2026 15.45
        "%Y-%m-%d %H.%M.%S",  # 2026-01-13 15.45.00
        "%Y-%m-%d %H.%M",  # 2026-01-13 15.45
        "%d/%m/%y %H.%M",  # 13/01/26 15.45
        "%d/%m/%Y %H.%M",  # 13/01/2026 15.45
        "%Y.%m.%d %H.%M.%S",  # 2026.01.13 15.45.00
    )

    def __init__(self, format_strings: Iterable[str] | None = None) -> None:
        self.format_strings = list(format_strings or self.DEFAULT_FORMATS)

    def execute(self, datetime_str: str, tz: ZoneInfo) -> datetime | None:
        """Parses a datetime from a string

        Args:
            datetime_str (str): user input
            tz (ZoneInfo): user timezone

        Returns:
            datetime | None: datetime object in UTC timezone or None if parsing failed
        """
        for format_string in self.format_strings:
            try:
                return (
                    datetime.strptime(datetime_str, format_string)
                    .replace(tzinfo=tz)
                    .astimezone(UTC)
                )
            except ValueError:
                pass
        return None
