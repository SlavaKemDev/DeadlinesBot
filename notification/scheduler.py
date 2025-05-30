import asyncio
from dataclasses import dataclass
from datetime import timedelta
from typing import List

from aiogram.exceptions import TelegramForbiddenError, TelegramRetryAfter

from bot.loader import *
from db.crud_deadline import DeadlineService
from db.crud_group import GroupService

from ai.model import Model
from db.crud_notifications import NotificationService


@dataclass
class NotificationTime:
    delta: timedelta
    value: str


notification_times: List[NotificationTime] = [
    NotificationTime(timedelta(days=14), "14 дней"),
    NotificationTime(timedelta(days=7), "7 дней"),
    NotificationTime(timedelta(days=3), "3 дня"),
    NotificationTime(timedelta(days=1), "1 день"),
    NotificationTime(timedelta(hours=12), "12 часов"),
    NotificationTime(timedelta(hours=6), "6 часов"),
    NotificationTime(timedelta(hours=3), "3 часа"),
    NotificationTime(timedelta(hours=1), "1 час"),
    NotificationTime(timedelta(minutes=30), "30 минут"),
    NotificationTime(timedelta(minutes=15), "15 минут"),
]

model = Model()


async def send_notification_safe(user_id: int, text: str) -> bool:
    try:
        await bot.send_message(user_id, text, parse_mode="Markdown")
        return True
    except TelegramForbiddenError:
        print(f"[x] Пользователь {user_id} заблокировал бота.")
        return False
    except TelegramRetryAfter as e:
        print(f"[!] Превышен лимит Telegram. Ждём {e.retry_after} сек...")
        await asyncio.sleep(e.retry_after)
        return await send_notification_safe(user_id, text)
    except Exception as e:
        print(f"[!] Ошибка при отправке уведомления пользователю {user_id}: {e}")
        return False


async def run_scheduler():
    while True:
        for notification_time in notification_times:
            seconds = int(notification_time.delta.total_seconds())
            deadlines = await DeadlineService.get_deadlines_within(seconds)

            for deadline in deadlines:
                print(f"[i] Отправка уведомлений по дедлайну: {deadline.name} ({deadline.date})")
                group_option = deadline.group_option
                group = group_option.group
                subscribers = await GroupService.get_subscribers(group_option)

                if not subscribers:
                    continue

                text = await model.create_notification(f"{group.name} {group_option.name}", deadline.name, notification_time.value)
                text += f"\n\n[{deadline.date.strftime('%d.%m.%Y %H:%M:%S')}] {deadline.name} ({group.name} {group_option.name})"

                print(text)

                for subscriber in subscribers:
                    await send_notification_safe(subscriber.id, text)

                await NotificationService.create(deadline, seconds)  # mark as notified

        await asyncio.sleep(60)  # Check every minute


if __name__ == "__main__":
    asyncio.run(run_scheduler())
