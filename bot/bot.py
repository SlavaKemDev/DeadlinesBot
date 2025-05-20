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

load_dotenv()

bot = Bot(os.environ['BOT_TOKEN'])

redis_client = redis.Redis(host="localhost", port=6379, db=0)
storage = RedisStorage(redis=redis_client, key_builder=DefaultKeyBuilder(with_bot_id=True))
dp = Dispatcher(storage=storage)


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("ПМИ. Подписаться")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
