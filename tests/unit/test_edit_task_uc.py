from datetime import UTC, datetime, timedelta
from typing import Iterator, TypeVar

import pytest

from date_task_bot.use_cases import EditTaskUseCase
from tests.factories import make_reminder

T = TypeVar("T")


def same_id_iter(
    *lists: list[T], key_field: str, check_elements: bool = True
) -> Iterator[tuple[T, ...]]:
    dicts = [{getattr(obj, key_field): obj for obj in lst} for lst in lists]

    keys = dicts[0].keys()
    if check_elements:
        for d in dicts:
            keys &= d.keys()

    for k in keys:
        yield tuple(d[k] for d in dicts)


@pytest.fixture
def edit_task_uc(task_repo_mock, reminder_repo_mock):
    return EditTaskUseCase(task_repo=task_repo_mock, reminder_repo=reminder_repo_mock)


def test_update_reminders(edit_task_uc: EditTaskUseCase):
    now = datetime.now(UTC)
    old_due_date = now + timedelta(hours=4)
    new_due_date = now + timedelta(hours=5)

    reminders_offsets = [
        timedelta(hours=-1),
        timedelta(hours=-2),
        timedelta(hours=-3),
    ]

    reminders = [
        make_reminder(offset_seconds=offset, remind_at=old_due_date + offset)
        for offset in reminders_offsets
    ]

    updated_reminders = edit_task_uc.update_reminders(
        reminders=reminders, new_due_date=new_due_date
    )

    for old_rem, updated_rem in same_id_iter(
        reminders, updated_reminders, key_field="id"
    ):
        assert old_rem.offset_seconds == updated_rem.offset_seconds

    for rem in updated_reminders:
        assert rem.remind_at == new_due_date + rem.offset_seconds


def test_update_reminders_skips_all_past(edit_task_uc: EditTaskUseCase):
    now = datetime.now(UTC)
    old_due_date = now + timedelta(hours=1)
    new_due_date = now - timedelta(hours=1)

    reminders_offsets = [
        timedelta(hours=-1),
        timedelta(hours=-2),
        timedelta(hours=-3),
    ]

    reminders = [
        make_reminder(offset_seconds=offset, remind_at=old_due_date + offset)
        for offset in reminders_offsets
    ]

    updated_reminders = edit_task_uc.update_reminders(reminders, new_due_date)

    assert updated_reminders == []


def test_update_reminders_empty_list(edit_task_uc: EditTaskUseCase):
    updated_reminders = edit_task_uc.update_reminders([], datetime.now(UTC))
    assert updated_reminders == []


def test_update_reminders_mixed(edit_task_uc: EditTaskUseCase):
    now = datetime.now(UTC)
    new_due_date = now + timedelta(hours=2)

    reminders = [
        make_reminder(offset_seconds=timedelta(hours=-3)),
        make_reminder(offset_seconds=timedelta(hours=-1)),
    ]

    updated_reminders = edit_task_uc.update_reminders(reminders, new_due_date)

    assert len(updated_reminders) == 1
    assert updated_reminders[0].offset_seconds == timedelta(hours=-1)
    assert updated_reminders[0].remind_at == new_due_date + timedelta(hours=-1)
