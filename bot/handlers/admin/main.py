import logging
import os
import random
from datetime import datetime, time, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import main
from bot.database.sqlite_db import get_admin_id, get_all_top_up, get_balance_user, unbalance,\
    top_up_balance
from bot.handlers.user.different import get_all_price_case, get_case, get_text_with_all_case,\
    send_message_all_admin, delete_cheque
from bot.keyboards import inline
from bot.keyboards.reply import back_kb, go_to_main_menu, menu_profile, select_type_market_kb, start_kb

from glQiwiApi import QiwiP2PClient
from glQiwiApi.qiwi.clients.p2p.types import Bill

import pytz


async def check_is_good(call: types.CallbackQuery):
    data = call.data.split("_")
    id_user = data[1]
    how_much = data[2]
    msg_id = data[3]
    
    await top_up_balance(how_much, id_user)
    for admin_id in await get_admin_id():
        await delete_cheque(admin_id, msg_id, text="Подтверждена!✅")
        
    await main.bot.send_message(id_user, f"Вам зачислено {how_much} на баланс")
    

async def check_is_not_ok(call: types.CallbackQuery):
    data = call.data.split("_")
    id_user = data[1]
    how_much = data[2]
    msg_id = data[3]
    
    await main.bot.send_message(id_user, f"❗Не было зачислено <b>{how_much}</b>руб\n"
                                         f"❌Чек не действителен, попробуйте ещё раз")
    
    for admin_id in await get_admin_id():
        await delete_cheque(admin_id, msg_id, text="Не подтверждена!❌")
    

def register_admin_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(check_is_good, text_contains='GoodCheque_')
    dp.register_callback_query_handler(check_is_not_ok, text_contains='NotOkCheque_')