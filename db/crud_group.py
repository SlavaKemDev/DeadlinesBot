from typing import List

from sqlalchemy.orm import selectinload
from sqlalchemy import select

from .models import User, Group, GroupOption, UserSubscription
from .session import AsyncSession
from aiogram.types import User as TeleUser


class GroupService:
    @staticmethod
    async def get_option_by_channel_id(channel_id: int) -> GroupOption:
        async with AsyncSession() as session:
            result = await session.execute(
                select(GroupOption)
                .options(selectinload(GroupOption.group))
                .where(GroupOption.telegram_channel_id == channel_id)
            )

            option = result.scalar_one_or_none()

            return option

    @staticmethod
    async def get_subscribers(group_option: GroupOption) -> List[User]:
        async with AsyncSession() as session:
            result = await session.execute(
                select(User).join(UserSubscription).where(
                    UserSubscription.group_option_id == group_option.id
                )
            )

            subscribers = result.scalars().all()

            return subscribers
