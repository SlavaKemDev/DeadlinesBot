from aiogram import F
from aiogram.types import Message

from bot.loader import *
from bot import keyboards
from bot.states import *
from bot import consts


@dp.message(AdminStates.admin_menu, F.text == consts.BTN_ADMIN_USERS)
async def manage_users(message: Message):
    # await state.set_state(AdminStates.manage_users)

    await message.answer("В разработке...")
