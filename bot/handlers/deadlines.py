from bot.loader import *
from aiogram import F
from aiogram.types import Message, CallbackQuery

from db.crud_user import *
from db.crud_deadline import *
from db.crud_group import *

from bot import keyboards
from collections import defaultdict

from bot.states import *
from bot import consts


def generate_deadlines_list(deadlines: List[Deadline], by_group: bool = True):
    text = "⏰ Предстоящие дедлайны:\n\n"

    if by_group:
        groups = defaultdict(list)

        for deadline in deadlines:
            name = f"{deadline.group_option.group.name} {deadline.group_option.name}"
            groups[name].append(deadline)

        keys = sorted(groups.keys())

        for group in keys:
            text += f"<b>{group}</b>\n"
            for deadline in sorted(groups[group], key=lambda d: d.date):
                text += f"<i>[{deadline.date.strftime('%d.%m.%Y %H:%M')}]</i> {deadline.name}\n"
            text += "\n"
    else:
        for deadline in sorted(deadlines, key=lambda d: d.date):
            name = f"{deadline.group_option.group.name}, {deadline.group_option.name}"
            text += f"<i>[{deadline.date.strftime('%d.%m.%Y %H:%M')}]</i> {deadline.name} ({name})\n"

    return text.strip()


@dp.message(MenuStates.main_menu, F.text == consts.BTN_UPCOMING_DEADLINES)
async def upcoming_deadlines(message: Message):
    user = await UserService.get_or_create(message.from_user)
    deadlines = await DeadlineService.get_deadlines_for_user(user)

    if not deadlines:
        await message.answer(consts.TEXT_NO_UPCOMING_DEADLINES)
        return

    text = generate_deadlines_list(deadlines, by_group=True)
    keyboard = keyboards.get_deadlines_list_keyboard(by_group=True)

    await message.answer(text, reply_markup=keyboard, parse_mode='HTML')


@dp.callback_query(MenuStates.main_menu, F.data.startswith("deadlines_"))
async def toggle_deadlines_grouping(callback: CallbackQuery):
    by_group = callback.data.endswith("1")
    user = await UserService.get_or_create(callback.from_user)
    deadlines = await DeadlineService.get_deadlines_for_user(user)

    if not deadlines:
        await callback.answer(consts.TEXT_NO_UPCOMING_DEADLINES)
        return

    text = generate_deadlines_list(deadlines, by_group=by_group)
    keyboard = keyboards.get_deadlines_list_keyboard(by_group=by_group)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    await callback.answer()
