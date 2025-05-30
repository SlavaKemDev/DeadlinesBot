from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.crud_user import *

from bot.loader import *
from bot import keyboards
from bot.states import *
from bot import consts


@dp.message(MenuStates.main_menu, F.text == consts.BTN_ADMIN_PANEL)
async def admin_panel(message: Message, state: FSMContext):
    user = await UserService.get_or_create(message.from_user)

    if not user.is_admin:
        await message.answer("У вас нет доступа к админ-панели.")
        return

    await state.set_state(AdminStates.admin_menu)
    await message.answer("Вы вошли в админ-панель", reply_markup=keyboards.get_admin_keyboard())


@dp.message(admin_states_filter, F.text == consts.BTN_ADMIN_EXIT)
async def exit_admin_panel(message: Message, state: FSMContext):
    await state.set_state(MenuStates.main_menu)

    user = await UserService.get_or_create(message.from_user)
    await message.answer("Вы вышли из админ-панели", reply_markup=keyboards.get_menu_keyboard(user))
