from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from date_task_bot.exceptions import (
    NOT_FOUND_MESSAGE,
    NotFoundException,
)
from date_task_bot.models import UserSettingsOrm

from .base_repository import BaseRepository
from .schemas import UserSettingsResponse, UserSettingsUpdate


class UserSettingsRepository(BaseRepository):

    async def get_by_user_id(
        self, user_id: str, load_timings: bool = False
    ) -> UserSettingsResponse:
        async with self.session_factory() as session:
            options = []
            if load_timings:
                options.append(selectinload(UserSettingsOrm.timings))
            stmt = (
                select(UserSettingsOrm)
                .options(*options)
                .where(UserSettingsOrm.user_id == user_id)
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            if result is None:
                raise NotFoundException(
                    NOT_FOUND_MESSAGE.format(
                        entity=f"Settings for user with chat_id={user_id}"
                    )
                )
            return UserSettingsResponse.model_validate(result)

    async def update(
        self, user_id: str, data: UserSettingsUpdate
    ) -> UserSettingsResponse:
        async with self.session_factory() as session:
            stmt = (
                update(UserSettingsOrm)
                .where(UserSettingsOrm.user_id == user_id)
                .values(timezone=data.timezone)
                .returning(UserSettingsOrm)
            )
            res = await session.execute(stmt)
            await session.commit()
            result = res.scalars().one_or_none()
            if not result:
                raise NotFoundException(
                    NOT_FOUND_MESSAGE.format(entity=f"User with chat_id={user_id}")
                )
            return UserSettingsResponse.model_validate(result)
