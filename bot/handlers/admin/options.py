from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.crud_deadline import DeadlineService
from db.crud_group import *

from bot.loader import *
from bot import keyboards
from bot.states import *


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("add_option"))
async def add_option(callback: CallbackQuery, state: FSMContext):
    group_id = int(callback.data.split("_")[2])
    group = await GroupService.get_group(group_id)

    if not group:
        await callback.answer("Группа не найдена.")
        return

    await state.set_state(AdminStates.add_option)
    await state.update_data(group_id=group_id)

    await callback.message.answer(f"Введите название опции для группы '{group.name}':")
    await callback.answer()


@dp.message(AdminStates.add_option)
async def process_add_option(message: Message, state: FSMContext):
    data = await state.get_data()
    group_id = data.get('group_id')

    if not group_id:
        await message.answer("Ошибка: не указана группа.")
        return

    group = await GroupService.get_group(group_id)
    if not group:
        await message.answer("Группа не найдена.")
        return

    option_name = message.text.strip()

    if not option_name:
        await message.answer("Название опции не может быть пустым.")
        return

    new_option = await GroupService.create_option(group, option_name)
    await message.answer(f"Опция '{new_option.name}' успешно добавлена в группу '{group.name}'!")
    await state.set_state(AdminStates.admin_menu)


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("option_"))
async def manage_option(callback: CallbackQuery):
    option_id = int(callback.data.split("_")[1])
    option = await GroupService.get_option(option_id)
    deadlines = await DeadlineService.get_deadlines(option)

    if not option:
        await callback.answer("Опция не найдена.")
        return

    group = option.group
    channel = f"t.me/c/{option.telegram_channel_id}/1" if option.telegram_channel_id else "Не указан"
    await callback.message.edit_text(
        f"{option.name} (Группа: {group.name})\n\nТелеграм канал: {channel}",
        reply_markup=keyboards.get_admin_option_keyboard(option, deadlines)
    )
    await callback.answer()


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("change_channel_"))
async def change_channel(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminStates.edit_option_channel)
    await state.update_data(option_id=int(callback.data.split("_")[2]))
    await callback.message.answer("Перешли любой пост из канала, который хочешь прикрепить")


@dp.message(AdminStates.edit_option_channel)
async def process_change_channel(message: Message, state: FSMContext):
    if not message.forward_from_chat:
        await message.answer("Пожалуйста, перешли пост из канала.")
        return

    channel_id = str(message.forward_from_chat.id)
    channel_name = message.forward_from_chat.title

    if not channel_id.startswith("-100"):
        await message.answer("Нужно переслать пост из канала!")

    channel_id = int(channel_id[3:])

    data = await state.get_data()
    option_id = data.get('option_id')

    if not option_id:
        await message.answer("Ошибка: не указана опция.")
        return

    option = await GroupService.get_option(option_id)
    if not option:
        await message.answer("Опция не найдена.")
        return

    option.telegram_channel_id = channel_id
    option.telegram_channel_name = channel_name
    await GroupService.update_option(option)

    await message.answer(f"Канал '{channel_name}' успешно прикреплен к опции '{option.name}'!")
    await state.set_state(AdminStates.admin_menu)
