from bot.loader import *
from bot import keyboards
from bot import consts
from bot.states import *

from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart

from db.crud_study_program import StudyProgramService
from db.crud_user import *


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    user = await UserService.get_or_create(message.from_user)

    if not user.study_program and not user.is_admin:  # Admin should add first study program
        study_programs = await StudyProgramService.get_list()

        await state.set_state(MenuStates.select_study_program)
        await message.answer(consts.TEXT_GREETING_CHOOSE_STUDY_PROGRAM,
                             reply_markup=keyboards.get_select_study_programs_keyboard(study_programs))
    else:
        await state.set_state(MenuStates.main_menu)
        await message.answer(consts.TEXT_GREETING, reply_markup=keyboards.get_menu_keyboard(user))
