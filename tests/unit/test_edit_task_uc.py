from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest

from date_task_bot.repositories.schemas import TaskUpdate
from date_task_bot.use_cases import EditTaskUseCase
from tests.factories import make_reminder, make_task


def same_id_iter[T](
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

    updated_reminders = edit_task_uc.update_reminders(
        reminders=reminders, new_due_date=new_due_date
    )

    assert updated_reminders == []


def test_update_reminders_empty_list(edit_task_uc: EditTaskUseCase):
    updated_reminders = edit_task_uc.update_reminders(
        reminders=[], new_due_date=datetime.now(UTC)
    )
    assert updated_reminders == []


def test_update_reminders_mixed(edit_task_uc: EditTaskUseCase):
    now = datetime.now(UTC)
    new_due_date = now + timedelta(hours=2)

    reminders = [
        make_reminder(offset_seconds=timedelta(hours=-3)),
        make_reminder(offset_seconds=timedelta(hours=-1)),
    ]

    updated_reminders = edit_task_uc.update_reminders(
        reminders=reminders, new_due_date=new_due_date
    )

    assert len(updated_reminders) == 1
    assert updated_reminders[0].offset_seconds == timedelta(hours=-1)
    assert updated_reminders[0].remind_at == new_due_date + timedelta(hours=-1)


async def test_displaying_reminders_text(edit_task_uc: EditTaskUseCase, task_repo_mock):
    task = make_task(reminders=[make_reminder()])
    task_no_reminders = task.model_copy(update={"reminders": []})

    task_repo_mock.get.return_value = task
    task_repo_mock.update.return_value = task_no_reminders

    res = await edit_task_uc.execute(
        user_id=task.user_id,
        data=TaskUpdate(id=task.id, text="new_text"),
    )
    assert len(res.reminders) == len(task.reminders)


async def test_displaying_reminders_date(edit_task_uc: EditTaskUseCase, task_repo_mock):
    now = datetime.now(UTC)
    old_due_date = now + timedelta(hours=4)
    new_due_date = now + timedelta(hours=5)
    offset = timedelta(hours=-1)
    task = make_task(
        reminders=[
            make_reminder(offset_seconds=offset, remind_at=old_due_date + offset)
        ]
    )
    task_no_reminders = task.model_copy(update={"reminders": []})

    task_repo_mock.get.return_value = task
    task_repo_mock.update.return_value = task_no_reminders

    res = await edit_task_uc.execute(
        user_id=task.user_id,
        data=TaskUpdate(id=task.id, due_date=new_due_date),
    )
    assert len(res.reminders) == len(task.reminders)
