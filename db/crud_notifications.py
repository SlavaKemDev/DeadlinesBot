from .models import Deadline, Notification
from .session import AsyncSession


class NotificationService:
    @staticmethod
    async def create(deadline: Deadline, seconds: int) -> None:
        async with AsyncSession() as session:
            notification = Notification(
                deadline_id=deadline.id,
                offset=seconds
            )
            session.add(notification)
            await session.commit()
