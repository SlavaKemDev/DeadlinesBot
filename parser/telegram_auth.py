import asyncio
from telethon import TelegramClient
import os
from dotenv import load_dotenv


load_dotenv()

API_ID = int(os.environ['API_ID'])
API_HASH = os.environ['API_HASH']
client = TelegramClient("parser_session", API_ID, API_HASH)


async def main():
    print("🔐 Авторизация через Telethon")
    await client.start()

    me = await client.get_me()
    print(f"✅ Успешно вошли как @{me.username or me.first_name}")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
