from .models import User
from .session import AsyncSession
from aiogram.types import User as TeleUser
from sqlalchemy import select, func


class UserService:
    @staticmethod
    async def get_or_create(tele_user: TeleUser) -> User:
        async with AsyncSession() as session:
            result = await session.execute(
                select(User).where(User.id == tele_user.id)
            )

            user = result.scalar_one_or_none()

            if user is None:
                user = User(
                    id=tele_user.id,
                    first_name=tele_user.first_name,
                    last_name=tele_user.last_name,
                    username=tele_user.username
                )

                session.add(user)
                await session.commit()

                return user
            else:
                user.first_name = tele_user.first_name
                user.last_name = tele_user.last_name
                user.username = tele_user.username
                await session.commit()

                return user

    @staticmethod
    async def users_count() -> int:
        async with AsyncSession() as session:
            result = await session.execute(select(func.count()).select_from(User))
            user_count = result.scalar_one()

            return user_count
