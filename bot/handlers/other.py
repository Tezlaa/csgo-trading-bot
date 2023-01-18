from aiogram import Dispatcher
from aiogram.types import Message

from bot import main
from bot.database.sqlite_db import create_profile
from bot.keyboards.reply import start_kb


async def bot_start(msg: Message):
    name = msg.from_user.username if msg.from_user.username != "None" else msg.from_user.first_name
    await msg.answer(f'Привет, {name}!\n'
                     f'Выбери интересующий пункт', reply_markup=start_kb)
    if msg.text[-1] != "t":
        ref_id = msg.text[7:]
        await create_profile(user_id=msg.from_user.id, username=name, referal=ref_id)
        try:
            await main.bot.send_message(ref_id, "По вашей ссылке зарегистрировался новый пользователь!")
        except Exception:
            pass
    else:
        await create_profile(user_id=msg.from_user.id, username=name)


def register_other_handlers(dp: Dispatcher):
    dp.register_message_handler(bot_start, commands=['start'])