from aiogram import F
from aiogram.types import Message

from db.crud_user import *

from bot.loader import *
from bot.states import *
from bot import consts


@dp.message(AdminStates.admin_menu, F.text == consts.BTN_ADMIN_STATS)
async def admin_stats(message: Message):
    # await state.set_state(AdminStates.statistics)

    total_users = await UserService.users_count()
    total_groups = -1  # await GroupService.count_groups()
    total_deadlines = -1  # await DeadlineService.count_deadlines()

    stats_text = (
        f"📊 **Статистика бота**\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"📚 Групп: {total_groups}\n"
        f"⏰ Дедлайнов: {total_deadlines}"
    )

    await message.answer(stats_text, parse_mode='Markdown')
