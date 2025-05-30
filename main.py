# run bot and parser in separate processes

import asyncio
from bot.bot import run_bot
from parser.telegram_parser import run_parser
from notification.scheduler import run_scheduler


async def main():
    # Run the bot and parser concurrently
    await asyncio.gather(
        run_bot(),
        run_parser(),
        run_scheduler()
    )


if __name__ == '__main__':
    asyncio.run(main())
