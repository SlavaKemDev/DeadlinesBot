from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.crud_group import *

from bot.loader import *
from bot import keyboards
from bot.states import *


@dp.message(AdminStates.admin_menu, F.text == keyboards.BTN_ADMIN_GROUPS)
async def manage_groups(message: Message):
    groups = await GroupService.get_list()

    await message.answer("Список групп:", reply_markup=keyboards.get_admin_groups(groups))


@dp.callback_query(AdminStates.admin_menu, F.data == "add_group")
async def add_group(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.add_group)

    await callback.message.answer("Введите название группы:")
    await callback.answer()


@dp.message(AdminStates.add_group)
async def process_add_group(message: Message, state: FSMContext):
    group_name = message.text.strip()

    if not group_name:
        await message.answer("Название группы не может быть пустым.")
        return

    new_group = await GroupService.create_group(group_name)
    await message.answer(f"Группа '{new_group.name}' успешно добавлена!")
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
