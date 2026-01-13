from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from date_task_bot.use_cases import ParseDatetimeFromTextUseCase


@pytest.fixture
def parse_datetime_from_text_uc():
    return ParseDatetimeFromTextUseCase()


@pytest.mark.parametrize(
    "text, expected_datetime, tz",
    [
        ("13.01.26 15:45", datetime(2026, 1, 13, 15, 45), ZoneInfo("Europe/London")),
        ("2026.01.13 15:45:00", datetime(2026, 1, 13, 6, 45), ZoneInfo("Asia/Tokyo")),
        ("2026-01-13 15.45.00", datetime(2026, 1, 13, 15, 45), ZoneInfo("UTC")),
        ("2026-01-13 15:45:00", datetime(2026, 1, 13, 15, 45), ZoneInfo("UTC")),
        ("2026-01-13 15:45", datetime(2026, 1, 13, 15, 45), ZoneInfo("UTC")),
        ("2026-01-13 15.45", datetime(2026, 1, 13, 15, 45), ZoneInfo("UTC")),
        ("invalid date", None, ZoneInfo("UTC")),
        ("32/01/2026 15:45", None, ZoneInfo("UTC")),
        ("13-13-2026 15:45", None, ZoneInfo("UTC")),
        ("2026-01-13T15:45", None, ZoneInfo("UTC")),
    ],
)
async def test_parse(
    parse_datetime_from_text_uc: ParseDatetimeFromTextUseCase,
    text: str,
    expected_datetime: datetime | None,
    tz: ZoneInfo,
):
    res = parse_datetime_from_text_uc.execute(datetime_str=text, tz=tz)

    if expected_datetime:
        expected_datetime = expected_datetime.replace(tzinfo=UTC)

    assert res == expected_datetime
