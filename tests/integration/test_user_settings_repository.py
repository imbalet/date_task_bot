from uuid import uuid4

from date_task_bot.models import UserSettingsOrm
from date_task_bot.repositories import UserSettingsRepository
from date_task_bot.repositories.schemas import (
    UserResponse,
    UserSettingsUpdate,
)


async def test_get_by_user_id(
    user_in_db: UserResponse,
    user_settings_repo: UserSettingsRepository,
):
    settings = await user_settings_repo.get_by_user_id(user_id=user_in_db.id)

    assert settings is not None


async def test_get_by_user_id_empty(
    user_settings_repo: UserSettingsRepository,
):
    res = await user_settings_repo.get_by_user_id(user_id="123")
    assert res is None


async def test_update(
    user_in_db: UserResponse,
    user_settings_repo: UserSettingsRepository,
    get_from_db_by_pk,
):
    settings = await user_settings_repo.get_by_user_id(user_id=user_in_db.id)
    assert settings
    settings_id = settings.id

    new_tz = "Europe/Moscow"
    settings = await user_settings_repo.update(
        data=UserSettingsUpdate(id=settings_id, timezone=new_tz)
    )
    assert settings

    from_db = await get_from_db_by_pk(UserSettingsOrm, settings.id)

    assert settings.timezone == new_tz
    assert from_db.timezone == new_tz


async def test_update_empty(user_settings_repo: UserSettingsRepository):
    new_tz = "Europe/Moscow"
    res = await user_settings_repo.update(
        data=UserSettingsUpdate(id=uuid4(), timezone=new_tz)
    )
    assert res is None
