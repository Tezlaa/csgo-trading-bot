import logging
import os
import random
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import main
from bot.database.sqlite_db import get_admin_id, unbalance

import pytz


async def send_offer_all_admin(login_or_link, amount, way_of_payment):
    tz = pytz.timezone('Europe/Moscow')
    time_now = str(datetime.now(tz)).split(".")[0]
    
    if login_or_link[:5] == "Трейд":
        login_or_link = login_or_link.split('"')[1]
    else:
        login_or_link = login_or_link.split(" ")[1]
    
    text_for_admin = (f"_❗Заявка на пополнение_\n***{time_now}***\n"
                      f"Пополнение: `{login_or_link}`\n Через {way_of_payment} на ***{amount}руб***")
    
    list_admin = await get_admin_id()
    for admin_id in list_admin:
        await main.bot.send_message(admin_id, text_for_admin, parse_mode='MARKDOWN')
    return


async def payment_p2p_qiwi(call: types.CallbackQuery, data: dict):
    comment = str(call.from_user.id) + "_" + str(random.randint(1000, 9999))
    bill = main.p2p.bill(amount=data["amount"], lifetime=15, comment=comment)
    
    await call.message.answer(f'Отправьте {data["amount"]}руб на счёт QIWI\n'
                              f'Ссылка: <a href="{bill.pay_url}">ССЫЛКА</a>\n'
                              f'Указанный комментарий к оплате: {comment}', parse_mode="HTML")