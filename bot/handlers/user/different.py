import logging
import os

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import main
from bot.database.sqlite_db import get_admin_id, unbalance
from bot.keyboards.inline import button_price, top_up_balance_steam, way_of_payment
from bot.keyboards.reply import open_market_kb, start_kb


async def send_all_admin(func, state):
    list_admin = await get_admin_id()
    
    async def wrapper():
        for admin_id in list_admin:
            func()
        await state.finish()