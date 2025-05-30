from typing import List

from sqlalchemy.orm import selectinload

from .models import User, Group, GroupOption, UserSubscription, Deadline
from .session import AsyncSession
from aiogram.types import User as TeleUser
from sqlalchemy import select
from datetime import datetime


class DeadlineService:
    @staticmethod
    async def get_deadlines(group_option: GroupOption) -> List[Deadline]:
        async with AsyncSession() as session:
            result = await session.execute(
                select(Deadline).where(
                    Deadline.group_option_id == group_option.id,
                    Deadline.date >= datetime.now()
                )
                .options(
                    selectinload(Deadline.group_option)
                    .selectinload(GroupOption.group)
                )
            )

            return result.scalars()

    @staticmethod
    async def get_deadlines_for_user(user: User):
        async with AsyncSession() as session:
            result = await session.execute(
                select(Deadline)
                .join(Deadline.group_option)
                .join(GroupOption.subscribers)
                .where(
                    UserSubscription.user_id == user.id,
                    Deadline.date >= datetime.now()
                )
                .options(
                    selectinload(Deadline.group_option).selectinload(GroupOption.group)
                )
                .order_by(Deadline.date)
            )

            return result.scalars().all()

    @staticmethod
    async def update_deadline(group_option: GroupOption, name: str, deadline_date: datetime) -> None:
        async with AsyncSession() as session:
            result = await session.execute(
                select(Deadline).where(
                    Deadline.group_option_id == group_option.id,
                    Deadline.name == name
                )
            )

            deadline = result.scalar_one_or_none()

            if deadline is None:
                deadline = Deadline(
                    group_option_id=group_option.id,
                    name=name,
                    date=deadline_date
                )
                session.add(deadline)
            else:
                deadline.date = deadline_date

            await session.commit()
