import asyncio

import telethon
from telethon import TelegramClient, events
import os
from dotenv import load_dotenv
from db.crud_group import *
from db.crud_deadline import *
from ai.model import Model
from aiogram import Bot
from pymorphy3 import MorphAnalyzer


load_dotenv()

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
client = TelegramClient("parser_session", API_ID, API_HASH)
model = Model()
bot_sender = Bot(os.environ['BOT_TOKEN'])
semaphore = asyncio.Semaphore(10)
morph = MorphAnalyzer()


async def send_message(chat_id, text, parse_mode='HTML'):
    """
    Send a message to a specific chat.
    """
    async with semaphore:
        try:
            await bot_sender.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
        except Exception as e:
            print(f"Error sending message to {chat_id}: {e}")


@client.on(events.NewMessage())
async def handler(event):
    message = event.message
    print(message)

    if not isinstance(message.peer_id, telethon.tl.types.PeerChannel):
        # Ignore messages from users
        return

    group_option = await GroupService.get_option_by_channel_id(message.peer_id.channel_id)

    if not group_option:
        # If this channels is not linked to any group, ignore the message
        return

    subscribers = await GroupService.get_subscribers(group_option)

    texts = []

    message_copy = message
    while message_copy:
        texts.append(f'[{message_copy.date.strftime("%d.%m.%Y %H:%M:%S")}] {message_copy.message}')
        message_copy = await message_copy.get_reply_message()

    texts.reverse()  # Reverse the order to have the oldest message first

    current_deadlines = await DeadlineService.get_deadlines(group_option)
    current_deadlines_list = [(deadline.name, deadline.date) for deadline in current_deadlines]
    current_deadlines_dict = {name: date for name, date in current_deadlines_list}

    deadlines = await model.get_response(texts, current_deadlines_list)  # Extract deadlines update from LLM

    for name, dt in deadlines:
        if name in current_deadlines_dict and current_deadlines_dict[name] == dt:
            continue

        await DeadlineService.update_deadline(group_option, name, dt)

        datv_group = morph.parse(group_option.group.name)[0].inflect({'datv'}).word
        datv_group = datv_group.capitalize()

        if name in current_deadlines_dict:
            message = f"📚 Обновление дедлайна по {datv_group} ({group_option.name}) \n\n{name}: {current_deadlines_dict[name].strftime('%d.%m.%Y %H:%M:%S')} -> {dt.strftime('%d.%m.%Y %H:%M:%S')}"
        else:
            message = f"⚡️Новый дедлайн по {datv_group} ({group_option.name})\n\n{name}: {dt.strftime('%d.%m.%Y %H:%M:%S')}"

        tasks = [send_message(subscriber.id, message) for subscriber in subscribers]
        await asyncio.gather(*tasks)


async def run_parser():
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(run_parser())
