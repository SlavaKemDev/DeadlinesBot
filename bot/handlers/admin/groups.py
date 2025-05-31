from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.crud_group import *

from bot.loader import *
from bot import keyboards
from bot.states import *
from bot import consts
from db.crud_study_program import StudyProgramService


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("add_group_"))
async def add_group(callback: CallbackQuery, state: FSMContext):
    study_program_id = int(callback.data.split("_")[2])
    study_program = await StudyProgramService.get_study_program(study_program_id)

    await state.set_state(AdminStates.add_group)
    await state.update_data(study_program_id=study_program_id)

    await callback.message.answer("Введите название группы:")
    await callback.answer()


@dp.message(AdminStates.add_group)
async def process_add_group(message: Message, state: FSMContext):
    data = await state.get_data()
    study_program_id = data.get('study_program_id')

    group_name = message.text.strip()

    if not group_name:
        await message.answer("Название группы не может быть пустым.")
        return

    study_program = await StudyProgramService.get_study_program(study_program_id)
    if not study_program:
        await message.answer("Образовательная программа не найдена.")
        return

    new_group = await GroupService.create_group(study_program, group_name)
    await message.answer(f"Группа '{new_group.name}' успешно добавлена в {study_program.name}!")
    await state.set_state(AdminStates.admin_menu)


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("group_"))
async def manage_group_options(callback: CallbackQuery):
    group_id = int(callback.data.split("_")[1])
    group = await GroupService.get_group(group_id)

    if not group:
        await callback.answer("Группа не найдена.")
        return

    await callback.message.edit_text(
        f"Группа: {group.name}",
        reply_markup=keyboards.get_admin_group_options(group)
    )
    await callback.answer()
