# run bot and parser in separate processes

import asyncio
from bot.bot import run_bot
from parser.telegram_parser import run_parser


async def main():
    # Run the bot and parser concurrently
    await asyncio.gather(
        run_bot(),
        run_parser()
    )


if __name__ == '__main__':
    asyncio.run(main())
