from aiogram import Dispatcher
from aiogram.types import Message

from bot.keyboards.reply import start_kb


async def bot_start(msg: Message):
    name = msg["from"]["username"]
    await msg.answer(f'Привет, {name if name != "None" else msg["from"]["firstname"]}!\n'
                     f'Выбери интересующий пункт', reply_markup=start_kb)
    

async def echo(msg: Message):
    await msg.answer(msg.text)


def register_other_handlers(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=['start'])
    dp.register_message_handler(echo, content_types=["text"])