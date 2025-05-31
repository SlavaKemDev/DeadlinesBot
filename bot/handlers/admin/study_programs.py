from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.crud_group import *

from bot.loader import *
from bot import keyboards
from bot.states import *
from bot import consts
from db.crud_study_program import StudyProgramService


@dp.message(AdminStates.admin_menu, F.text == consts.BTN_ADMIN_GROUPS)
async def manage_study_programs(message: Message):
    study_programs = await StudyProgramService.get_list()

    await message.answer("Список образовательных программ:", reply_markup=keyboards.get_admin_study_programs(study_programs))


@dp.callback_query(AdminStates.admin_menu, F.data == "add_study_program")
async def add_study_program(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_study_program)
    await callback.message.answer("Введите название образовательной программы:")
    await callback.answer()


@dp.message(AdminStates.add_study_program)
async def process_add_study_program(message: Message, state: FSMContext):
    program_name = message.text.strip()

    if not program_name:
        await message.answer("Название образовательной программы не может быть пустым.")
        return

    new_program = await StudyProgramService.create_study_program(program_name)
    await message.answer(f"Образовательная программа '{new_program.name}' успешно добавлена!")
    await state.set_state(AdminStates.admin_menu)


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("study_program_"))
async def manage_study_program(callback: CallbackQuery):
    program_id = int(callback.data.split("_")[2])
    study_program = await StudyProgramService.get_study_program(program_id)

    if not study_program:
        await callback.answer("Образовательная программа не найдена.")
        return

    await callback.message.edit_text(
        f"Образовательная программа: {study_program.name}",
        reply_markup=keyboards.get_admin_study_program_options(study_program)
    )
    await callback.answer()
