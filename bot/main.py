import csv
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils import executor

from bot.database.sqlite_db import sql_start
from bot.handlers import register_all_handlers

from glQiwiApi import QiwiP2PClient


async def __on_start_up(dp: Dispatcher) -> None:
    await sql_start()
    register_all_handlers(dp)


def start_bot():
    global bot, p2p_qiwi, case_cs, skin_trade, social

    case_cs = {}
    skin_trade = {}
    social = {}
       
    with open('files_for_admin/social.csv', "r", encoding="utf8") as f:
        reader = csv.reader(f)
        for name_social, link_social in reader:
            social[name_social] = link_social
    with open('files_for_admin/case_price.csv', "r", encoding="utf8") as f:
        reader = csv.reader(f)
        for case, price in reader:
            case_cs[case] = int(price)
    with open('files_for_admin/skins.csv', "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for skin, price in reader:
            skin_trade[skin] = int(price)
            
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    
    """
    ----if run via file 'run.py'----
    from files_for_admin.important import token_telegram, token_qiwi
    
    bot = Bot(token=token_telegram, parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())
    p2p_qiwi = QiwiP2PClient(secret_p2p=token_qiwi)
    """
    
    bot = Bot(token=os.getenv("TOKEN"), parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())
    p2p_qiwi = QiwiP2PClient(secret_p2p=os.getenv("TOKEN_QIWI"))
    
    executor.start_polling(dp, skip_updates=True, on_startup=__on_start_up)