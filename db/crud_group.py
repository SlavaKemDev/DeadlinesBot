from typing import List

from sqlalchemy.orm import selectinload
from sqlalchemy import select

from .models import User, Group, GroupOption, UserSubscription
from .session import AsyncSession
from aiogram.types import User as TeleUser


class GroupService:
    @staticmethod
    async def get_list():
        async with AsyncSession() as session:
            result = await session.execute(
                select(Group).options(selectinload(Group.options))
            )

            groups = result.scalars().all()

            return groups

    @staticmethod
    async def get_subscriptions(user: User) -> List[GroupOption]:
        async with AsyncSession() as session:
            result = await session.execute(
                select(GroupOption).join(UserSubscription).where(
                    UserSubscription.user_id == user.id
                ).options(selectinload(GroupOption.group))
            )

            subscriptions = result.scalars().all()

            return subscriptions

    @staticmethod
    async def get_option(group_option_id: int):
        async with AsyncSession() as session:
            result = await session.execute(
                select(GroupOption).where(GroupOption.id == group_option_id)
            )

            option = result.scalar_one_or_none()

            return option

    @staticmethod
    async def toggle_subscription(user: User, group_option: GroupOption):
        async with AsyncSession() as session:
            # get subscription in current group if exists
            result = await session.execute(
                select(UserSubscription)
                .join(UserSubscription.group_option)
                .join(GroupOption.group)
                .where(
                    UserSubscription.user_id == user.id,
                    GroupOption.group_id == group_option.group_id
                )
                .options(selectinload(UserSubscription.group_option))
            )

            subscriptions = result.scalars().all()
            has_subscription = group_option.id in {sub.group_option.id for sub in subscriptions}

            for subscription in subscriptions:
                await session.delete(subscription)

            if not has_subscription:  # if not subscribed, create new subscription
                session.add(UserSubscription(
                    user_id=user.id,
                    group_option_id=group_option.id
                ))

            await session.commit()

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
