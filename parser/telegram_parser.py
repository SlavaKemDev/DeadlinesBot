import asyncio
from telethon import TelegramClient, events
import os
from dotenv import load_dotenv


load_dotenv()

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
client = TelegramClient("parser_session", API_ID, API_HASH)


@client.on(events.NewMessage())
async def handler(event):
    message = event.message
    print(message)


async def main():
    await client.start()
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
