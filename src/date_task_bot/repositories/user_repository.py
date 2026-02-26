from logging import getLogger

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from date_task_bot.exceptions import AlreadyExistsException, EntityEnum
from date_task_bot.models import TaskOrm, UserOrm, UserSettingsOrm
from date_task_bot.schemas import User

from .base_repository import BaseRepository
from .schemas import UserCreate, UserResponse

logger = getLogger(__name__)


class UserRepository(BaseRepository):
    async def create(self, user: UserCreate) -> User:
        async with self.session_factory() as session:
            try:
                new = UserOrm(id=user.id)
                session.add(new)
                await session.flush()
                await session.commit()
                return UserResponse.model_validate(new)
            except IntegrityError as e:
                await session.rollback()
                logger.exception("Integrity error in UserRepository", exc_info=True)
                raise AlreadyExistsException(
                    entity=EntityEnum.USER, data={"id": user.id}
                ) from e

    async def get(
        self,
        id: str,
        load_tasks: bool = False,
        load_reminders: bool = False,
        load_settings: bool = False,
        load_offsets: bool = False,
    ) -> User | None:
        async with self.session_factory() as session:
            options = []
            if load_tasks:
                options.append(selectinload(UserOrm.tasks))
            if load_reminders:
                options.append(
                    selectinload(UserOrm.tasks).selectinload(TaskOrm.reminders)
                )
            if load_settings:
                options.append(selectinload(UserOrm.settings))
            if load_offsets:
                options.append(
                    selectinload(UserOrm.settings).selectinload(UserSettingsOrm.timings)
                )

            res = await session.get(UserOrm, id, options=options)
            if res is None:
                return None
            return UserResponse.model_validate(res)
