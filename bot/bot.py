import asyncio

from .loader import *

from .handlers.common import *
from .handlers.deadlines import *
from .handlers.subscriptions import *
from .handlers.admin.panel import *
from .handlers.admin.stats import *
from .handlers.admin.users import *
from .handlers.admin.groups import *
from .handlers.admin.options import *
from .handlers.admin.deadlines import *


async def run_bot():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(run_bot())
