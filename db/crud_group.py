from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlalchemy import select

from .models import User, Group, GroupOption, UserSubscription, StudyProgram
from .session import AsyncSession
from aiogram.types import User as TeleUser


class GroupService:
    @staticmethod
    async def get_list(study_program: Optional[StudyProgram]) -> List[Group]:
        if not study_program:
            return []

        async with AsyncSession() as session:
            result = await session.execute(
                select(Group)
                .where(Group.study_program_id == study_program.id)
                .options(selectinload(Group.options))
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
    async def get_group(group_id: int) -> Group:
        async with AsyncSession() as session:
            result = await session.execute(
                select(Group)
                .where(Group.id == group_id)
                .options(selectinload(Group.options))
            )

            group = result.scalar_one_or_none()

            return group

    @staticmethod
    async def get_option(group_option_id: int):
        async with AsyncSession() as session:
            result = await session.execute(
                select(GroupOption).where(GroupOption.id == group_option_id)
                .options(selectinload(GroupOption.group))
            )

            option = result.scalar_one_or_none()

            return option

    @staticmethod
    async def update_option(group_option: GroupOption) -> None:
        async with AsyncSession() as session:
            await session.merge(group_option)
            await session.commit()

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

    @staticmethod
    async def create_group(study_program: StudyProgram, name: str) -> Group:
        async with AsyncSession() as session:
            group = Group(
                study_program_id=study_program.id,
                name=name
            )

            session.add(group)
            await session.commit()
            await session.refresh(group)
            return group

    @staticmethod
    async def create_option(group: Group, name: str) -> GroupOption:
        async with AsyncSession() as session:
            option = GroupOption(
                group_id=group.id,
                name=name
            )

            session.add(option)
            await session.commit()
            await session.refresh(option)
            return option
