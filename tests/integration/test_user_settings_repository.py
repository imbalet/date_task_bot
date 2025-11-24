import pytest

from date_task_bot.exceptions import NotFoundException
from date_task_bot.models import UserSettingsOrm
from date_task_bot.repositories import UserSettingsRepository
from date_task_bot.repositories.schemas import (
    UserResponse,
    UserSettingsUpdate,
)
from tests.integration.utils import (
    get_from_db_by_pk,
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
    with pytest.raises(NotFoundException):
        await user_settings_repo.get_by_user_id(user_id="123")


async def test_update(
    async_session_factory,
    user_in_db: UserResponse,
    user_settings_repo: UserSettingsRepository,
):
    new_tz = "Europe/Moscow"
    settings = await user_settings_repo.update(
        user_id=user_in_db.id, data=UserSettingsUpdate(timezone=new_tz)
    )

    from_db = await get_from_db_by_pk(
        async_session_factory, UserSettingsOrm, settings.id
    )

    assert settings.timezone == new_tz
    assert from_db.timezone == new_tz


async def test_update_empty(user_settings_repo: UserSettingsRepository):
    new_tz = "Europe/Moscow"
    with pytest.raises(NotFoundException):
        await user_settings_repo.update(
            user_id="123", data=UserSettingsUpdate(timezone=new_tz)
        )
