import asyncio

from dotenv import load_dotenv
import os
from typing import Dict
from datetime import datetime
from aiogram import Bot, Dispatcher, F
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, StateFilter, Command, CommandObject
from aiogram.utils.deep_linking import create_start_link
import redis.asyncio as redis
import json
from copy import deepcopy
import random
import hashlib

from db.crud_user import *
from db.crud_deadline import *
from db.crud_group import *

from . import keyboards
from collections import defaultdict

load_dotenv()

bot = Bot(os.environ['BOT_TOKEN'])

redis_client = redis.Redis(host="localhost", port=6379, db=0)
storage = RedisStorage(redis=redis_client, key_builder=DefaultKeyBuilder(with_bot_id=True))
dp = Dispatcher(storage=storage)


# State Definitions


class MenuStates(StatesGroup):
    main_menu = State()


class AdminStates(StatesGroup):
    admin_menu = State()

    add_group = State()
    edit_group_name = State()

    add_option = State()
    edit_option_name = State()
    edit_option_channel = State()

    add_deadline = State()
    edit_deadline_name = State()
    edit_deadline_date = State()


admin_states_filter = StateFilter(*[state for state in AdminStates.__all_states__])


# Command Handlers


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.set_state(MenuStates.main_menu)

    user = await UserService.get_or_create(message.from_user)
    await message.answer("""Привет! 👋
Я — бот для мониторинга дедлайнов на ПМИ ВШЭ.

📌 Я слежу за сообщениями в каналах дисциплин и автоматически сообщаю, когда появляется новый дедлайн или обновляется старый.
🗓 Также ты можешь в любой момент посмотреть список всех актуальных дедлайнов.

Выбери действие с помощью кнопок ниже""", reply_markup=keyboards.get_menu_keyboard(user))


def generate_deadlines_list(deadlines: List[Deadline], by_group: bool = True):
    text = "⏰ Предстоящие дедлайны:\n\n"

    if by_group:
        groups = defaultdict(list)

        for deadline in deadlines:
            name = f"{deadline.group_option.group.name} ({deadline.group_option.name})"
            groups[name].append(deadline)

        keys = sorted(groups.keys())

        for group in keys:
            text += f"<b>{group}</b>\n"
            for deadline in sorted(groups[group], key=lambda d: d.date):
                text += f"<i>[{deadline.date.strftime('%d.%m.%Y %H:%M')}]</i> {deadline.name}\n"
            text += "\n"
    else:
        for deadline in sorted(deadlines, key=lambda d: d.date):
            name = f"{deadline.group_option.group.name}, {deadline.group_option.name}"
            text += f"<i>[{deadline.date.strftime('%d.%m.%Y %H:%M')}]</i> {deadline.name} ({name})\n"

    return text.strip()


@dp.message(MenuStates.main_menu, F.text == keyboards.BTN_UPCOMING_DEADLINES)
async def upcoming_deadlines(message: Message, state: FSMContext):
    user = await UserService.get_or_create(message.from_user)
    deadlines = await DeadlineService.get_deadlines_for_user(user)

    if not deadlines:
        await message.answer("Нет предстоящих дедлайнов.")
        return

    text = generate_deadlines_list(deadlines, by_group=True)
    keyboard = keyboards.get_deadlines_list_keyboard(by_group=True)

    await message.answer(text, reply_markup=keyboard, parse_mode='HTML')


@dp.callback_query(MenuStates.main_menu, F.data.startswith("deadlines_"))
async def toggle_deadlines_grouping(callback: CallbackQuery, state: FSMContext):
    by_group = callback.data.endswith("1")
    user = await UserService.get_or_create(callback.from_user)
    deadlines = await DeadlineService.get_deadlines_for_user(user)

    if not deadlines:
        await callback.answer("Нет предстоящих дедлайнов.")
        return

    text = generate_deadlines_list(deadlines, by_group=by_group)
    keyboard = keyboards.get_deadlines_list_keyboard(by_group=by_group)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')
    await callback.answer()


@dp.message(MenuStates.main_menu, F.text == keyboards.BTN_MY_SUBSCRIPTIONS)
async def my_subscriptions(message: Message, state: FSMContext):
    user = await UserService.get_or_create(message.from_user)

    groups_list = await GroupService.get_list()
    subscriptions = await GroupService.get_subscriptions(user)

    kb = keyboards.get_subscriptions_keyboard(subscriptions, groups_list)

    await message.answer("Выбери, по каким дисциплинам хочешь получать уведомления", reply_markup=kb)


@dp.callback_query(MenuStates.main_menu, F.data.startswith("option_"))
async def toggle_subscription(callback: CallbackQuery, state: FSMContext):
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


@dp.message(MenuStates.main_menu, F.text == keyboards.BTN_ADMIN_PANEL)
async def admin_panel(message: Message, state: FSMContext):
    user = await UserService.get_or_create(message.from_user)

    if not user.is_admin:
        await message.answer("У вас нет доступа к админ-панели.")
        return

    await state.set_state(AdminStates.admin_menu)
    await message.answer("Вы вошли в админ-панель", reply_markup=keyboards.get_admin_keyboard())


@dp.message(admin_states_filter, F.text == keyboards.BTN_ADMIN_EXIT)
async def exit_admin_panel(message: Message, state: FSMContext):
    await state.set_state(MenuStates.main_menu)

    user = await UserService.get_or_create(message.from_user)
    await message.answer("Вы вышли из админ-панели", reply_markup=keyboards.get_menu_keyboard(user))


@dp.message(AdminStates.admin_menu, F.text == keyboards.BTN_ADMIN_STATS)
async def admin_stats(message: Message, state: FSMContext):
    # await state.set_state(AdminStates.statistics)

    total_users = await UserService.users_count()
    total_groups = -1  # await GroupService.count_groups()
    total_deadlines = -1  # await DeadlineService.count_deadlines()

    stats_text = (
        f"📊 **Статистика бота**\n\n"
        f"👥 Пользователей: {total_users}\n"
        f"📚 Групп: {total_groups}\n"
        f"⏰ Дедлайнов: {total_deadlines}"
    )

    await message.answer(stats_text, parse_mode='Markdown')


@dp.message(AdminStates.admin_menu, F.text == keyboards.BTN_ADMIN_USERS)
async def manage_users(message: Message, state: FSMContext):
    # await state.set_state(AdminStates.manage_users)

    await message.answer("В разработке...")


@dp.message(AdminStates.admin_menu, F.text == keyboards.BTN_ADMIN_GROUPS)
async def manage_groups(message: Message, state: FSMContext):
    # await state.set_state(AdminStates.manage_groups)

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
async def manage_group_options(callback: CallbackQuery, state: FSMContext):
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
async def manage_option(callback: CallbackQuery, state: FSMContext):
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


async def run_bot():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_bot())
