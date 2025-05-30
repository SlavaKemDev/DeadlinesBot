from bot.loader import *
from bot import keyboards
from bot import consts
from bot.states import *

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart

from db.crud_user import *


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(MenuStates.main_menu)

    user = await UserService.get_or_create(message.from_user)
    await message.answer(consts.TEXT_GREETING, reply_markup=keyboards.get_menu_keyboard(user))
