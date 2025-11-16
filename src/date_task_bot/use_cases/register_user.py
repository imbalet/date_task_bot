from dataclasses import dataclass

from date_task_bot.repositories import UserRepository
from date_task_bot.repositories.schemas import UserCreate
from date_task_bot.schemas import User


@dataclass
class RegisterUserUseCaseResult:
    """
    user_exists (bool): True if user already exists.\n
    user (User): User object.
    """

    user_exists: bool
    user: User


class RegisterUserUseCase:
    def __init__(self, user_repo: UserRepository) -> None:
        self.user_repo = user_repo

    async def execute(self, data: UserCreate):
        user = await self.user_repo.get(id=data.id, load_settings=True)

        if user:
            return RegisterUserUseCaseResult(user_exists=True, user=user)

        new_user = await self.user_repo.create(data)
        return RegisterUserUseCaseResult(user_exists=False, user=new_user)
