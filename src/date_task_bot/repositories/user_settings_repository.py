from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from date_task_bot.models import UserSettingsOrm
from date_task_bot.schemas import UserSettings

from .base_repository import BaseRepository
from .schemas import UserSettingsResponse, UserSettingsUpdate


class UserSettingsRepository(BaseRepository):
    async def get_by_user_id(
        self, *, user_id: str, load_offsets: bool = False
    ) -> UserSettings | None:
        async with self.session_factory() as session:
            options = []
            if load_offsets:
                options.append(selectinload(UserSettingsOrm.timings))
            stmt = (
                select(UserSettingsOrm)
                .options(*options)
                .where(UserSettingsOrm.user_id == user_id)
            )
            res = await session.execute(stmt)
            result = res.scalar_one_or_none()
            if result is None:
                return None
            return UserSettingsResponse.model_validate(result)

    async def update(self, *, data: UserSettingsUpdate) -> UserSettings | None:
        async with self.session_factory() as session:
            stmt = (
                update(UserSettingsOrm)
                .where(UserSettingsOrm.id == data.id)
                .values(timezone=data.timezone)
                .returning(UserSettingsOrm)
            )
            res = await session.execute(stmt)
            await session.commit()
            result = res.scalars().one_or_none()
            if not result:
                return None
            return UserSettingsResponse.model_validate(result)
