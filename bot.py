import asyncio
import logging

from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import handlers

from config_reader import config
from database import init_db



logging.basicConfig(level=logging.DEBUG)


async def main():
    await init_db()
    bot = Bot(token=config.bot_token.get_secret_value())
    dp = Dispatcher(storage=MemoryStorage())

    dp["started_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")

    dp.include_router(handlers.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
