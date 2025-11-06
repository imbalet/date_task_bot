from sqlalchemy.exc import IntegrityError

from date_task_bot.models import UserOrm

from .base_repository import BaseRepository
from .exceptions import ALREADY_EXISTS_MESSAGE, AlreadyExistsException
from .schemas import UserCreate, UserResponse


class UserRepository(BaseRepository):

    async def create(self, user: UserCreate) -> UserResponse:
        async with self.session_factory() as session:
            try:
                new = UserOrm(id=user.id)
                session.add(new)
                await session.commit()
                await session.refresh(new)
                return UserResponse.model_validate(new)
            except IntegrityError:
                await session.rollback()
                raise AlreadyExistsException(
                    ALREADY_EXISTS_MESSAGE.format(entity=f"User with chat_id={user.id}")
                )

    async def get(self, id: str) -> UserResponse | None:
        async with self.session_factory() as session:
            res = await session.get(UserOrm, id)
            if res is None:
                return None
            return UserResponse.model_validate(res)
