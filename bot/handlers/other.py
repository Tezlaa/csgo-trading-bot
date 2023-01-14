from aiogram import Dispatcher
from aiogram.types import Message

from bot.database.sqlite_db import create_profile
from bot.keyboards.reply import start_kb


async def bot_start(msg: Message):
    name = msg["from"]["username"] if msg["from"]["username"] != "None" else msg["from"]["firstname"]
    await msg.answer(f'Привет, {name}!\n'
                     f'Выбери интересующий пункт', reply_markup=start_kb)
    await create_profile(user_id=msg["from"]["id"], username=name)


def register_other_handlers(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=['start'])