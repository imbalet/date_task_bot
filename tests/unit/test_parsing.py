from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from date_task_bot.use_cases import ParseDateTimeUseCase


@pytest.fixture
def parse_datetime_uc():
    return ParseDateTimeUseCase()


@pytest.mark.parametrize(
    "text, expected_datetime, now",
    [
        # hours
        ("12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 13, 0)),
        ("12:00", datetime(2025, 1, 1, 12, 0), datetime(2025, 1, 1, 12, 0)),
        ("12:00", datetime(2025, 1, 1, 12, 0), datetime(2025, 1, 1, 11, 0)),
        ("15:00", datetime(2025, 1, 1, 15, 0), datetime(2025, 1, 1, 11, 0)),
        ("23:00", datetime(2025, 1, 1, 23, 0), datetime(2025, 1, 1, 11, 0)),
        ("09:00", datetime(2025, 1, 1, 9, 0), datetime(2025, 1, 1, 8, 0)),
        ("9:00", datetime(2025, 1, 1, 9, 0), datetime(2025, 1, 1, 8, 0)),
        # ("в 12 часов", datetime(2025, 1, 1, 12, 0), datetime(2025, 1, 1, 11, 0)), not working now
        # hours with minutes
        ("12:01", datetime(2025, 1, 1, 12, 1), datetime(2025, 1, 1, 11, 0)),
        ("12:59", datetime(2025, 1, 1, 12, 59), datetime(2025, 1, 1, 11, 0)),
        ("9:30", datetime(2025, 1, 1, 9, 30), datetime(2025, 1, 1, 8, 0)),
        # tomorrow
        ("завтра в 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 11, 0)),
        ("завтра в 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 12, 0)),
        ("завтра в 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 13, 0)),
        ("завтра в 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 23, 59)),
        ("завтра в 9:00", datetime(2025, 1, 2, 9, 0), datetime(2025, 1, 1, 8, 0)),
        # dates
        ("2 января 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 11, 0)),
        # ("2.01 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 11, 0)), not working now
        # ("02.01 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 11, 0)),
        # ("02.01.25 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 11, 0)),
        # ("02.01.2025 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 11, 0)),
        ("3 января 12:00", datetime(2025, 1, 3, 12, 0), datetime(2025, 1, 1, 11, 0)),
        (
            "31 декабря 12:00",
            datetime(2025, 12, 31, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        ("1 января 12:00", datetime(2025, 1, 1, 12, 0), datetime(2025, 1, 1, 11, 0)),
        # relative dated
        (
            "через 2 дня 12:00",
            datetime(2025, 1, 3, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через два дня 12:00",
            datetime(2025, 1, 3, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через 10 дней 12:00",
            datetime(2025, 1, 11, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через десять дня 12:00",
            datetime(2025, 1, 11, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через 2 дня 12:00",
            datetime(2025, 2, 1, 12, 0),
            datetime(2025, 1, 30, 11, 0),
        ),
        (
            "через 365 дней 12:00",
            datetime(2026, 1, 1, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через неделю 12:00",
            datetime(2025, 1, 8, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через 1 неделю 12:00",
            datetime(2025, 1, 8, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через одну неделю 12:00",
            datetime(2025, 1, 8, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через две недели 12:00",
            datetime(2025, 1, 15, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        (
            "через 2 недели 12:00",
            datetime(2025, 1, 15, 12, 0),
            datetime(2025, 1, 1, 11, 0),
        ),
        # without time relative
        ("завтра", datetime(2025, 1, 2, 11, 0), datetime(2025, 1, 1, 11, 0)),
        ("послезавтра", datetime(2025, 1, 3, 11, 0), datetime(2025, 1, 1, 11, 0)),
        ("через два дня", datetime(2025, 1, 3, 11, 0), datetime(2025, 1, 1, 11, 0)),
        # without time date
        ("2 января", datetime(2025, 1, 2, 0, 0), datetime(2025, 1, 1, 11, 0)),
        # other year
        (
            "31 декабря 23:00",
            datetime(2025, 12, 31, 23, 0),
            datetime(2025, 12, 30, 22, 0),
        ),
        ("1 января 0:30", datetime(2026, 1, 1, 0, 30), datetime(2025, 12, 31, 23, 0)),
        # short months
        ("2 янв 12:00", datetime(2025, 1, 2, 12, 0), datetime(2025, 1, 1, 11, 0)),
        ("2 янв.", datetime(2025, 1, 2, 0, 0), datetime(2025, 1, 1, 11, 0)),
        # relative minutes/hours
        ("через 3 часа", datetime(2025, 1, 1, 14, 0), datetime(2025, 1, 1, 11, 0)),
        ("через 90 минут", datetime(2025, 1, 1, 12, 30), datetime(2025, 1, 1, 11, 0)),
        # midnight
        ("0:00", datetime(2025, 1, 2, 0, 0), datetime(2025, 1, 1, 11, 0)),
        # day of week
        ("понедельник 12:00", datetime(2025, 1, 6, 12, 0), datetime(2025, 1, 1, 11, 0)),
        ("следующий понедельник 12:00", datetime(2025, 1, 6, 12, 0), datetime(2025, 1, 1, 11, 0)),
        ("среда 12:00", datetime(2025, 1, 8, 12, 0), datetime(2025, 1, 1, 11, 0)),
        ("среда 10:00", datetime(2025, 1, 8, 10, 0), datetime(2025, 1, 1, 11, 0)),
    ],
)
def test_parse(
    parse_datetime_uc: ParseDateTimeUseCase,
    text: str,
    expected_datetime: datetime,
    now: datetime,
):

    original_build_settings = parse_datetime_uc._build_settings

    def build_settings_mock(cls, user_tz_str):
        settings = original_build_settings(user_tz_str)
        settings["RELATIVE_BASE"] = now.replace(tzinfo=None)
        return settings

    with patch.object(ParseDateTimeUseCase, "_build_settings", build_settings_mock):
        res = parse_datetime_uc.execute("UTC", text)

    assert res.success
    assert res.date == expected_datetime.replace(tzinfo=UTC)
