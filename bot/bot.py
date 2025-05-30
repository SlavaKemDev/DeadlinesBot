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


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
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
            text += f"**{group}**\n"
            for deadline in sorted(groups[group], key=lambda d: d.date):
                text += f"- {deadline.name}: {deadline.date.strftime('%d.%m.%Y %H:%M')}\n"
            text += "\n"
    else:
        for deadline in sorted(deadlines, key=lambda d: d.date):
            name = f"{deadline.group_option.group.name}, {deadline.group_option.name}"
            text += f"- {deadline.name} ({name}): {deadline.date.strftime('%d.%m.%Y %H:%M')}\n"

    return text.strip()


@dp.message(F.text == keyboards.BTN_UPCOMING_DEADLINES)
async def upcoming_deadlines(message: Message, state: FSMContext):
    user = await UserService.get_or_create(message.from_user)
    deadlines = await DeadlineService.get_deadlines_for_user(user)

    if not deadlines:
        await message.answer("Нет предстоящих дедлайнов.")
        return

    text = generate_deadlines_list(deadlines, by_group=True)
    keyboard = keyboards.get_deadlines_list_keyboard(by_group=True)

    await message.answer(text, reply_markup=keyboard, parse_mode='Markdown')


@dp.callback_query(F.data.startswith("deadlines_"))
async def toggle_deadlines_grouping(callback: CallbackQuery, state: FSMContext):
    by_group = callback.data.endswith("1")
    user = await UserService.get_or_create(callback.from_user)
    deadlines = await DeadlineService.get_deadlines_for_user(user)

    if not deadlines:
        await callback.answer("Нет предстоящих дедлайнов.")
        return

    text = generate_deadlines_list(deadlines, by_group=by_group)
    keyboard = keyboards.get_deadlines_list_keyboard(by_group=by_group)

    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode='Markdown')
    await callback.answer()


@dp.message(F.text == keyboards.BTN_MY_SUBSCRIPTIONS)
async def my_subscriptions(message: Message, state: FSMContext):
    user = await UserService.get_or_create(message.from_user)

    groups_list = await GroupService.get_list()
    subscriptions = await GroupService.get_subscriptions(user)

    kb = keyboards.get_subscriptions_keyboard(subscriptions, groups_list)

    await message.answer("Выбери, по каким дисциплинам хочешь получать уведомления", reply_markup=kb)


@dp.callback_query(F.data.startswith("option_"))
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


async def run_bot():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(run_bot())
