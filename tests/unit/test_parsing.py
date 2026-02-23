from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import pytest

from date_task_bot.use_cases import ParseDateTimeUseCase


@pytest.fixture
def parse_datetime_uc():
    return ParseDateTimeUseCase()


def get_datetime(
    y: int = 2025, month: int = 1, day: int = 1, hour: int = 12, min: int = 0
) -> datetime:
    """Generates datetime object.

    Args:
        y (int, optional): year. Defaults to 2025.
        mn (int, optional): month. Defaults to 1.
        d (int, optional): day. Defaults to 1.
        h (int, optional): hours. Defaults to 12.
        m (int, optional): minutes. Defaults to 0.

    Returns:
        datetime: datetime
    """
    return datetime(year=y, month=month, day=day, hour=hour, minute=min)


# alias
dt = get_datetime

# (string, expected_datetime, actual_datetime)

hours_check = (
    ("12:00", dt(day=2, hour=12), dt(day=1, hour=13)),
    ("12:00", dt(day=1, hour=12), dt(day=1, hour=12)),
    ("12:00", dt(day=1, hour=12), dt(day=1, hour=11)),
    ("15:00", dt(day=1, hour=15), dt(day=1, hour=11)),
    ("23:00", dt(day=1, hour=23), dt(day=1, hour=11)),
    ("09:00", dt(day=1, hour=9), dt(day=1, hour=8)),
    ("9:00", dt(day=1, hour=9), dt(day=1, hour=8)),
    # ("в 12 часов", dt(day=1, hour=12, min=0), dt( month=1, day=1, hour=11, min=0)), not working now
)

hours_with_minutes_check = (
    ("12:01", dt(hour=12, min=1), dt(hour=11, min=0)),
    ("12:59", dt(hour=12, min=59), dt(hour=11, min=0)),
    ("9:30", dt(hour=9, min=30), dt(hour=8, min=0)),
)

tomorrow_check = (
    ("завтра в 12:00", dt(day=2, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("завтра в 12:00", dt(day=2, hour=12, min=0), dt(day=1, hour=12, min=0)),
    ("завтра в 12:00", dt(day=2, hour=12, min=0), dt(day=1, hour=13, min=0)),
    ("завтра в 12:00", dt(day=2, hour=12, min=0), dt(day=1, hour=23, min=59)),
    ("завтра в 9:00", dt(day=2, hour=9, min=0), dt(day=1, hour=8, min=0)),
)

dates_check = (
    (
        "2 января 12:00",
        dt(month=1, day=2, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    # ("2.01 12:00", dt( month=1, day=2, hour=12, min=0), dt( month=1, day=1, hour=11, min=0)), not working now
    # ("02.01 12:00", dt( month=1, day=2, hour=12, min=0), dt( month=1, day=1, hour=11, min=0)),
    # ("02.01.25 12:00", dt( month=1, day=2, hour=12, min=0), dt( month=1, day=1, hour=11, min=0)),
    # ("02.01.2025 12:00", dt( month=1, day=2, hour=12, min=0), dt( month=1, day=1, hour=11, min=0)),
    (
        "3 января 12:00",
        dt(month=1, day=3, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    (
        "31 декабря 12:00",
        dt(month=12, day=31, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    (
        "1 января 12:00",
        dt(month=1, day=1, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    # without time
    ("2 января", dt(month=1, day=2, hour=0, min=0), dt(month=1, day=1, hour=11, min=0)),
    # short months
    (
        "2 янв 12:00",
        dt(month=1, day=2, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    ("2 янв.", dt(month=1, day=2, hour=0, min=0), dt(month=1, day=1, hour=11, min=0)),
)

relative_dates_check = (
    ("через 2 дня 12:00", dt(day=3, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("через два дня 12:00", dt(day=3, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("через 10 дней 12:00", dt(day=11, hour=12, min=0), dt(day=1, hour=11, min=0)),
    (
        "через десять дня 12:00",
        dt(month=1, day=11, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    (
        "через 2 дня 12:00",
        dt(month=2, day=1, hour=12, min=0),
        dt(month=1, day=30, hour=11, min=0),
    ),
    (
        "через 365 дней 12:00",
        dt(y=2026, month=1, day=1, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    ("через неделю 12:00", dt(day=8, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("через 1 неделю 12:00", dt(day=8, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("через одну неделю 12:00", dt(day=8, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("через две недели 12:00", dt(day=15, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("через 2 недели 12:00", dt(day=15, hour=12, min=0), dt(day=1, hour=11, min=0)),
    (
        "через месяц 12:00",
        dt(month=2, day=28, hour=12, min=0),
        dt(month=1, day=31, hour=11, min=0),
    ),
    (
        "через месяц 12:00",
        dt(month=2, day=28, hour=12, min=0),
        dt(month=1, day=29, hour=11, min=0),
    ),
    (
        "через месяц 12:00",
        dt(month=2, day=28, hour=12, min=0),
        dt(month=1, day=28, hour=11, min=0),
    ),
    ("через 2 дня 11:00", dt(day=3, hour=11, min=0), dt(day=1, hour=11, min=0)),
    ("через 2 дня в 11:00", dt(day=3, hour=11, min=0), dt(day=1, hour=11, min=0)),
    ("через неделю 0:00", dt(day=8, hour=0, min=0), dt(day=1, hour=11, min=0)),
    (
        "через месяц 00:00",
        dt(month=2, day=28, hour=0, min=0),
        dt(month=1, day=31, hour=11, min=0),
    ),
)

without_time_relative_check = (
    ("завтра", dt(day=2, hour=11, min=0), dt(day=1, hour=11, min=0)),
    ("послезавтра", dt(day=3, hour=11, min=0), dt(day=1, hour=11, min=0)),
    ("послепослезавтра", dt(day=4, hour=11, min=0), dt(day=1, hour=11, min=0)),
    ("через два дня", dt(day=3, hour=11, min=0), dt(day=1, hour=11, min=0)),
)

year_check = (
    (
        "2 января 12:00 2027 года",
        dt(y=2027, month=1, day=2, hour=12, min=0),
        dt(y=2025, month=1, day=1, hour=11, min=0),
    ),
    (
        "2 января 12:00 2027",
        dt(y=2027, month=1, day=2, hour=12, min=0),
        dt(y=2025, month=1, day=1, hour=11, min=0),
    ),
    (
        "2 января 12:00 2027 г",
        dt(y=2027, month=1, day=2, hour=12, min=0),
        dt(y=2025, month=1, day=1, hour=11, min=0),
    ),
    (
        "2 января 12:00 2027г",
        dt(y=2027, month=1, day=2, hour=12, min=0),
        dt(y=2025, month=1, day=1, hour=11, min=0),
    ),
    # other year
    (
        "31 декабря 23:00",
        dt(y=2025, month=12, day=31, hour=23, min=0),
        dt(y=2025, month=12, day=30, hour=22, min=0),
    ),
    (
        "1 января 0:30",
        dt(y=2026, month=1, day=1, hour=0, min=30),
        dt(y=2025, month=12, day=31, hour=23, min=0),
    ),
)

relative_time_check = (
    # hours
    ("через час", dt(hour=12, min=0), dt(hour=11, min=0)),
    ("через один час", dt(hour=12, min=0), dt(hour=11, min=0)),
    ("через 1 час", dt(hour=12, min=0), dt(hour=11, min=0)),
    ("через 3 часа", dt(hour=14, min=0), dt(hour=11, min=0)),
    ("через 24 часа", dt(day=2, hour=11, min=0), dt(day=1, hour=11, min=0)),
    ("через 25 часов", dt(day=2, hour=12, min=0), dt(day=1, hour=11, min=0)),
    # minutes
    ("через минуту", dt(hour=11, min=1), dt(hour=11, min=0)),
    ("через 1 минуту", dt(hour=11, min=1), dt(hour=11, min=0)),
    ("через 59 минут", dt(hour=11, min=59), dt(hour=11, min=0)),
    ("через 60 минут", dt(hour=12, min=0), dt(hour=11, min=0)),
    ("через 61 минуту", dt(hour=12, min=1), dt(hour=11, min=0)),
)

day_of_week_check = (
    ("понедельник 12:00", dt(day=6, hour=12, min=0), dt(day=1, hour=11, min=0)),
    (
        "следующий понедельник 12:00",
        dt(day=6, hour=12, min=0),
        dt(day=1, hour=11, min=0),
    ),
    ("среда 12:00", dt(day=8, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("среда 10:00", dt(day=8, hour=10, min=0), dt(day=1, hour=11, min=0)),
)

same_weekday_check = (
    # now = среда (2025-01-01)
    ("среда 12:00", dt(day=8, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("среда 23:59", dt(day=8, hour=23, min=59), dt(day=1, hour=11, min=0)),
)

weekday_short_check = (
    ("пн 12:00", dt(day=6, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("вт 12:00", dt(day=7, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("ср 12:00", dt(day=8, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("чт 12:00", dt(day=2, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("пт 12:00", dt(day=3, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("сб 12:00", dt(day=4, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("вс 12:00", dt(day=5, hour=12, min=0), dt(day=1, hour=11, min=0)),
)

month_only_check = (
    (
        "март 12:00",
        dt(month=3, day=1, hour=12, min=0),
        dt(month=1, day=1, hour=11, min=0),
    ),
    ("март", dt(month=3, day=1, hour=0, min=0), dt(month=1, day=1, hour=11, min=0)),
)

day_month_next_year_check = (
    (
        "1 января 12:00",
        dt(y=2026, month=1, day=1, hour=12, min=0),
        dt(y=2025, month=1, day=2, hour=11, min=0),
    ),
    (
        "31 декабря 12:00",
        dt(y=2025, month=12, day=31, hour=12, min=0),
        dt(y=2025, month=1, day=1, hour=11, min=0),
    ),
)
leap_year_check = (
    (
        "29 февраля 12:00",
        dt(y=2028, month=2, day=29, hour=12, min=0),
        dt(y=2026, month=1, day=30, hour=11, min=0),
    ),
)

noise_check = (
    ("  завтра   в   12:00  ", dt(day=2, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("ЗАВТРА В 12:00", dt(day=2, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("Завтра, в 12:00", dt(day=2, hour=12, min=0), dt(day=1, hour=11, min=0)),
    ("через   2   дня   12:00", dt(day=3, hour=12, min=0), dt(day=1, hour=11, min=0)),
)

edge_cases = (
    ("0:00", dt(day=2, hour=0, min=0), dt(day=1, hour=11, min=0)),
    ("11:00", dt(day=1, hour=11, min=0), dt(day=1, hour=11, min=0)),
    ("11:01", dt(day=1, hour=11, min=1), dt(day=1, hour=11, min=0)),
    ("10:59", dt(day=2, hour=10, min=59), dt(day=1, hour=11, min=0)),
    ("23:59", dt(day=1, hour=23, min=59), dt(day=1, hour=11, min=0)),
    ("00:01", dt(day=2, hour=0, min=1), dt(day=1, hour=11, min=0)),
)

cross_period_check = (
    # next year
    ("9:00", dt(hour=9), dt(y=2024, month=12, day=31, hour=23)),
    ("через 3 часа", dt(hour=2), dt(y=2024, month=12, day=31, hour=23)),
    ("среда", dt(hour=0), dt(y=2024, month=12, day=31, hour=23)),
    # next month
    ("9:00", dt(month=2, hour=9), dt(day=31, hour=23)),
    ("через 3 часа", dt(month=2, hour=2), dt(day=31, hour=23)),
    ("суббота", dt(month=2, day=1, hour=0), dt(day=31, hour=10)),
    # next week
    ("9:00", dt(day=6, hour=9), dt(day=5, hour=23)),
    ("через 3 часа", dt(day=6, hour=2), dt(day=5, hour=23)),
)


@pytest.mark.parametrize(
    "text, expected_datetime_, now",
    [
        *hours_check,
        *hours_with_minutes_check,
        *tomorrow_check,
        *dates_check,
        *relative_dates_check,
        *without_time_relative_check,
        *year_check,
        *relative_time_check,
        *day_of_week_check,
        *same_weekday_check,
        *weekday_short_check,
        *month_only_check,
        *day_month_next_year_check,
        *leap_year_check,
        *noise_check,
        *edge_cases,
        *cross_period_check,
    ],
)
@pytest.mark.parametrize(
    "timezone",
    ["UTC", "Europe/Moscow", "Asia/Tokyo"],
)
def test_parse(
    parse_datetime_uc: ParseDateTimeUseCase,
    text: str,
    expected_datetime_: datetime,
    now: datetime,
    timezone: str,
):
    # convert to UTC
    expected_datetime = expected_datetime_.replace(
        tzinfo=ZoneInfo(timezone)
    ).astimezone(UTC)

    res = parse_datetime_uc.execute(
        user_tz_str=timezone, text=text, now=now.replace(tzinfo=None)
    )

    assert res.success
    assert res.date == expected_datetime
