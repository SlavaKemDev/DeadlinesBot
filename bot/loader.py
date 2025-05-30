from dotenv import load_dotenv
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage, DefaultKeyBuilder
import redis.asyncio as redis

load_dotenv()

bot = Bot(os.environ['BOT_TOKEN'])

redis_client = redis.Redis(host="localhost", port=6379, db=0)
storage = RedisStorage(redis=redis_client, key_builder=DefaultKeyBuilder(with_bot_id=True))
dp = Dispatcher(storage=storage)
