import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from bot.database.sqlite_db import sql_start
from bot.handlers import register_all_handlers

from pyqiwip2p import QiwiP2P


async def __on_start_up(dp: Dispatcher) -> None:
    await sql_start()
    register_all_handlers(dp)


def start_bot():
    global bot, p2p
    bot = Bot(token=os.getenv("TOKEN"), parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())
    p2p = QiwiP2P(auth_key=os.getenv("TOKEN_QIWI"))
    
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)