import os
from datetime import datetime

from aiogram import types
from aiogram.types import InlineKeyboardButton
from bot.keyboards.inline import check_cheque_admin, offer_steam

from bot import main
from bot.database.sqlite_db import get_admin_id

import pytz


async def send_message_all_admin(text_for_admin: str, photo=False):
    tz = pytz.timezone('Europe/Moscow')
    time_now = f'Время заявки: ***{str(datetime.now(tz)).split(".")[0]}***'
    
    list_admin = await get_admin_id()
    for admin_id in list_admin:
        await main.bot.send_message(chat_id=admin_id, text=time_now, parse_mode='MARKDOWN')
        await main.bot.send_message(chat_id=admin_id, text=text_for_admin, parse_mode='MARKDOWN')
        if photo:
            await main.bot.send_photo(admin_id, photo)
    return


async def offer_steam_notification(text_for_admin: str, user_id: str):
    tz = pytz.timezone('Europe/Moscow')
    time_now = f'Время заявки: ***{str(datetime.now(tz)).split(".")[0]}***'
    
    list_admin = await get_admin_id()
    msg_id = []
    for admin_id in list_admin:
        await main.bot.send_message(chat_id=admin_id, text=time_now, parse_mode='MARKDOWN')
    for index, admin_id in enumerate(list_admin):
        msg_id.append((await main.bot.send_message(admin_id, 'Получение...')).message_id)
        await main.bot.delete_message(admin_id, msg_id[index])
        msg_id[index] += len(list_admin)
    for admin_id in list_admin:
        await main.bot.send_message(chat_id=admin_id, text=text_for_admin, parse_mode='MARKDOWN',
                                    reply_markup=offer_steam(user_id=user_id, msg_id=msg_id))
    return


async def check_cheque(photo, how_much: str, id_user: str):
    list_admin = await get_admin_id()
    msg_id = []
    for index, admin_id in enumerate(list_admin):
        msg_id.append((await main.bot.send_message(admin_id, 'Получение...')).message_id)
        await main.bot.delete_message(admin_id, msg_id[index])
        msg_id[index] += len(list_admin)
    for admin_id in list_admin:
        await main.bot.send_photo(admin_id, photo, reply_markup=check_cheque_admin(how_much, id_user, msg_id))


async def delete_cheque(admin_id: str, msg_id: str, text: str):
    msg_id = msg_id[1:-1]
    for msg_id_admin in msg_id.split(", "):
        try:
            await main.bot.edit_message_reply_markup(chat_id=admin_id,
                                                     message_id=msg_id_admin,
                                                     reply_markup=types.InlineKeyboardMarkup().add(
                                                         InlineKeyboardButton(text, callback_data="+")))
        except Exception:
            pass


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


async def send_photo_with_trade_skin(call):
    await call.message.delete()
    directory = "files_for_admin/photo_for_trade"
    photos = list()
    formats = ['.jpg', '.jpeg', '.png']
    
    for i in formats:
        for j in filter(lambda x: x.endswith(i), os.listdir(directory)):
            photos.append(j)
    for i in photos:
        with open(f"{directory}/{i}", 'rb') as photo:
            await main.bot.send_photo(chat_id=call.message.chat.id, photo=photo)


def get_skin() -> dict:
    return main.skin_trade

    
def get_case() -> dict:
    return main.case_cs
