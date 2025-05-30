from bot.loader import *
from bot import keyboards
from bot import consts
from bot.states import *

from aiogram import F
from aiogram.types import Message, CallbackQuery

from db.crud_user import *
from db.crud_group import *


@dp.message(MenuStates.main_menu, F.text == consts.BTN_MY_SUBSCRIPTIONS)
async def my_subscriptions(message: Message):
    user = await UserService.get_or_create(message.from_user)

    groups_list = await GroupService.get_list()
    subscriptions = await GroupService.get_subscriptions(user)

    kb = keyboards.get_subscriptions_keyboard(subscriptions, groups_list)

    await message.answer("Выбери, по каким дисциплинам хочешь получать уведомления", reply_markup=kb)


@dp.callback_query(MenuStates.main_menu, F.data.startswith("option_"))
async def toggle_subscription(callback: CallbackQuery):
    group_option_id = int(callback.data.split("_")[1])

    user = await UserService.get_or_create(callback.from_user)
    group_option = await GroupService.get_option(group_option_id)

    if not group_option:
        await callback.answer("Ошибка: опция группы не найдена.")
        return

    await GroupService.toggle_subscription(user, group_option)

    text = "Выбери, по каким дисциплинам хочешь получать уведомления"
    kb = keyboards.get_subscriptions_keyboard(
        await GroupService.get_subscriptions(user),
        await GroupService.get_list()
    )

    await callback.message.edit_text(text, reply_markup=kb)
    await callback.answer()
