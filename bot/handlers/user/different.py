import logging
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


from bot import main
from bot.database.sqlite_db import get_admin_id, unbalance

import pytz


async def send_message_all_admin(text_for_admin: str):
    tz = pytz.timezone('Europe/Moscow')
    time_now = f'Время заявки: ***{str(datetime.now(tz)).split(".")[0]}***'
    
    list_admin = await get_admin_id()
    for admin_id in list_admin:
        await main.bot.send_message(admin_id, time_now, parse_mode='MARKDOWN')
        await main.bot.send_message(admin_id, text_for_admin, parse_mode='MARKDOWN')
    return


async def get_text_with_all_case() -> str:
    case = get_case()
    
    text = ""
    for item, price in case.items():
        text += f"Кейс: '{item}' - {price}руб\n"
    
    return text


async def get_all_price_case(all_case_from_user: dict, price_on_case: dict) -> int:
    price = 0
    for all_case in all_case_from_user:
        for case, count in all_case.items():
            for case_dp, price_dp in price_on_case.items():
                if case == case_dp:
                    price += (count * price_dp)
    
    return price
            

async def payment_p2p_qiwi(call: types.CallbackQuery, data: dict):
    comment = str(call.from_user.id) + "_" + str(random.randint(1000, 9999))
    bill = main.p2p.bill(amount=data["amount"], lifetime=15, comment=comment)
    
    await call.message.answer(f'Отправьте {data["amount"]}руб на счёт QIWI\n'
                              f'Ссылка: <a href="{bill.pay_url}">ССЫЛКА</a>\n'
                              f'Указанный комментарий к оплате: {comment}', parse_mode="HTML")
    
    
def get_case() -> dict:
    case = {"Грёзы и кошмары": 5, "Решающий момент": 2, "Змеиный укус": 3, "Разлом": 4,
            "Расколотая сеть": 7, "Спектр": 2, "Хромированный кейс №3": 6}
    return case
