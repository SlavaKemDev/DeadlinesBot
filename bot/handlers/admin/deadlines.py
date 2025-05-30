from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from db.crud_deadline import DeadlineService
from db.crud_group import *

from bot.loader import *
from bot import keyboards
from bot.states import *

from datetime import datetime


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("add_deadline_"))
async def add_deadline(callback: CallbackQuery, state: FSMContext):
    option_id = int(callback.data.split("_")[2])
    option = await GroupService.get_option(option_id)

    if not option:
        await callback.answer("Опция не найдена.")
        return

    await state.set_state(AdminStates.add_deadline)
    await state.update_data(option_id=option_id)

    await callback.message.answer(f"Введите название дедлайна для опции '{option.name}':")
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


@dp.callback_query(AdminStates.admin_menu, F.data.startswith("deadline_"))
async def manage_deadline(callback: CallbackQuery, state: FSMContext):
    deadline_id = int(callback.data.split("_")[1])
    deadline = await DeadlineService.get_deadline(deadline_id)

    if not deadline:
        await callback.answer("Дедлайн не найден.")
        return

    option = deadline.group_option
    group = option.group

    await callback.message.edit_text(
        f"Дедлайн: {deadline.name}\n"
        f"Дата: {deadline.date.strftime('%d.%m.%Y %H:%M')}\n"
        f"📃{group.name} ({option.name})",
        reply_markup=keyboards.get_admin_deadline_keyboard(deadline)
    )
    await callback.answer()


@dp.message(AdminStates.add_deadline)
async def process_add_deadline(message: Message, state: FSMContext):
    data = await state.get_data()
    option_id = data.get('option_id')

    if not option_id:
        await message.answer("Ошибка: не указана опция.")
        return

    option = await GroupService.get_option(option_id)
    if not option:
        await message.answer("Опция не найдена.")
        return

    if not data.get('deadline_name'):
        deadline_name = message.text.strip()

        if not deadline_name:
            await message.answer("Название дедлайна не может быть пустым.")
            return

        await message.answer("Введите дату дедлайна в формате ДД.ММ.ГГГГ ЧЧ:ММ (например, 01.01.2023 12:00):")
        await state.update_data(deadline_name=deadline_name)
    else:
        deadline_name = data['deadline_name']
        deadline_date_str = message.text.strip()

        try:
            deadline_date = datetime.strptime(deadline_date_str, "%d.%m.%Y %H:%M")
        except ValueError:
            await message.answer("Неверный формат даты. Используйте ДД.ММ.ГГГГ ЧЧ:ММ.")
            return

        await DeadlineService.update_deadline(option, deadline_name, deadline_date)
        await message.answer(f"Дедлайн '{deadline_name}' успешно добавлен для опции '{option.name}'!")
        await state.set_state(AdminStates.admin_menu)
        await state.set_data({})
