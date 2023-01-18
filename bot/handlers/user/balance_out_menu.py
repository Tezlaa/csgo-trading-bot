import logging
import os
import random
from datetime import datetime, time, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import main
from bot.database.sqlite_db import get_admin_id, unbalance, get_balance_user, get_all_top_up,\
    count_ref
from bot.handlers.user.different import get_all_price_case, get_case, get_text_with_all_case,\
    send_message_all_admin, check_cheque
from bot.keyboards import inline
from bot.keyboards.reply import back_kb, go_to_main_menu, select_type_market_kb, start_kb, menu_profile

from glQiwiApi import QiwiP2PClient
from glQiwiApi.qiwi.clients.p2p.types import Bill

import pytz


class FsmWantOutBalanceFromSteam(StatesGroup):
    name_steam = State()
    other_data_for_offer = State()


class FsmSelectCase(StatesGroup):
    witch_case = State()
    how_much = State()
    name_steam = State()
    other_data_for_offer = State()


async def balance_out(msg: types.Message):
    if type(msg) == types.CallbackQuery:
        msg.answer = msg.message.edit_text
    elif msg.text != 'Назад':
        await msg.answer('Вывести баланс', reply_markup=back_kb)
     
    await msg.answer('Вывод возможен от 100Р.'
                     'Вы сможете вывести средства на Qiwi, ЮMoney, СберБанк, Тинькофф, МТС, Yota и другие кошельки.'
                     'Комиссию при переводе не оплачиваем!', reply_markup=inline.balance_out_start)


async def balance_out_from_steam(call: types.CallbackQuery, state: FsmWantOutBalanceFromSteam):
    await call.message.edit_text('Вы должны купить и передать нам Mann Co. Supply Crate Key из Team Fortress 2.'
                                 'За каждый ключ вы получите 96Р.', reply_markup=inline.wont_to_balance_out_on_steam)


async def out_key(call: types.CallbackQuery):  # need link on trade
    trade_link = 'https://www.google.com.ua/'
    await call.message.edit_text(f'Отправьте обмен по этой <a href="{trade_link}">ССЫЛКА</a>',
                                 parse_mode="HTML", reply_markup=inline.check_on_trade)
    

async def check_user_on_trade(call: types.CallbackQuery):
    await FsmWantOutBalanceFromSteam.name_steam.set()
    await call.message.edit_text("Напишите в чат с ботом одним сообщением ваш ник из Steam.")


async def set_name_steam(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name_steam"] = msg.text
    
    await msg.answer("Напишите в чат с ботом одним сообщением следующие данные:\n"
                     "1) Название вашего кошелька.\n"
                     "2) Номер карты или номер телефона привязанного к кошельку.\n"
                     "3) Ф.И.О получателя.\n"
                     "4) Комментарий (необязательно).\n")
    
    await FsmWantOutBalanceFromSteam.next()


async def set_message_by_user(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["message_by_user"] = msg.text
    
    username = msg.from_user.username if msg.from_user.username != "None" else msg.from_user.first_name
    
    text_for_admin = (f"_❗Заявка на вывод ключей_\n"
                      f"Nickname steam: `{data['name_steam']}`\n"
                      f"Telegram для связи: `@{username}`\n"
                      f"Данные пользователя: {data['message_by_user']}")
    
    await msg.answer("Ваш запрос получен. В течении 24 часов мы отправим деньги."
                     "Если возникнут проблемы, наш сотрудник свяжется с вами.",
                     reply_markup=inline.go_to_balance_out_start)
    await state.finish()
    await send_message_all_admin(text_for_admin)


async def sell_case(call: types.CallbackQuery):
    await FsmSelectCase.witch_case.set()
    await call.message.edit_text(f"Выберите кейсы из вашего инвентаря\n"
                                 f"{await get_text_with_all_case()}",
                                 reply_markup=inline.sell_case_start)


async def set_case(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Выберите кейс:", reply_markup=inline.get_case_inline_kb(get_case()))


async def set_how_case(call: types.CallbackQuery, state: FSMContext):
    case = call.data.split("_")[1]
    async with state.proxy() as data:
        try:
            data["all_case"] += [{case: 0}]
        except KeyError:
            data["all_case"] = []
            data["all_case"] += [{case: 0}]
                    
        data["case"] = case
    await call.message.edit_text(f"Выберите количество кейсов «{case}»", reply_markup=inline.count_case())

    await FsmSelectCase.next()


async def info_about_adding(call: types.CallbackQuery, state: FSMContext):
    how_much = int(call.data.split("_")[1])
    async with state.proxy() as data:
        data["all_case"][len(data["all_case"]) - 1][data["case"]] += how_much
        
    text_with_all_case = ""
    for all_case in data["all_case"]:
        for case, count in all_case.items():
            text_with_all_case += f'Кейс:  {case} - {count}шт.\n'
        
    await call.message.edit_text(f"Вы добавили:\n"
                                 f"{text_with_all_case}",
                                 reply_markup=inline.select_path_kb)


async def adding_case_path(call: types.CallbackQuery, state: FSMContext):  # need trade link
    if call.data == 'add_case':
        await FsmSelectCase.first()
        await sell_case(call)
    else:
        trade_link = 'https://www.google.com.ua/'
        async with state.proxy() as data:
            await call.message.edit_text(f"После обмена вы получите: "
                                         f"{await get_all_price_case(data['all_case'], get_case())}руб\n\n"
                                         f"Отправьте трейд по этой <a href=\"{trade_link}\">ССЫЛКЕ</a>",
                                         reply_markup=inline.check_on_trade)
        await FsmSelectCase.next()


async def check_trade_sell_case(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Напишите в чат с ботом одним сообщением ваш ник из Steam.")


async def set_name_steam_sell_case(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name_steam"] = msg.text
    
    await msg.answer("Напишите в чат с ботом одним сообщением следующие данные:\n"
                     "1) Название вашего кошелька.\n"
                     "2) Номер карты или номер телефона привязанного к кошельку.\n"
                     "3) Ф.И.О получателя.\n"
                     "4) Комментарий (необязательно).\n")
    
    await FsmSelectCase.next()


async def set_message_by_user_sell_case(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["message_by_user"] = msg.text
    
    username = msg.from_user.username if msg.from_user.username != "None" else msg.from_user.first_name
        
    price_all_case = await get_all_price_case(data['all_case'], get_case())
    text_with_all_case = ""
    for all_case in data["all_case"]:
        for case, count in all_case.items():
            text_with_all_case += f'   *{case}* - *{count}*шт.\n'
    
    text_for_admin = (f"_❗Заявка на вывод ключей_\n"
                      f"Nickname steam: `{data['name_steam']}`\n"
                      f"Telegram для связи: `@{username}`\n"
                      f"Цена кейсов: *{price_all_case}руб\n*"
                      f"Кейсы:\n{text_with_all_case}"
                      f"\nДанные пользователя: *{data['message_by_user']}*")
    
    await msg.answer("Ваш запрос получен. В течении 24 часов мы отправим деньги."
                     "Если возникнут проблемы, наш сотрудник свяжется с вами.",
                     reply_markup=inline.go_to_balance_out_start)
    await state.finish()
    await send_message_all_admin(text_for_admin)


def register_balance_out_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(balance_out, text=['cancel_trade'], state="*")
    dp.register_message_handler(balance_out, Text(equals=['Вывести баланс', 'Назад']))
    
    dp.register_callback_query_handler(balance_out_from_steam, text="want_balance_out_from_steam")
    dp.register_callback_query_handler(out_key, text='out_key')
    dp.register_callback_query_handler(check_user_on_trade, text='check_trade')
    dp.register_message_handler(set_name_steam, state=FsmWantOutBalanceFromSteam.name_steam)
    dp.register_message_handler(set_message_by_user, state=FsmWantOutBalanceFromSteam.other_data_for_offer)
    dp.register_callback_query_handler(sell_case, text='want_sell')
    dp.register_callback_query_handler(set_case, text='select_case', state=FsmSelectCase)
    dp.register_callback_query_handler(set_how_case, text_contains='case_', state=FsmSelectCase.witch_case)
    dp.register_callback_query_handler(info_about_adding, text_contains="count_", state=FsmSelectCase.how_much)
    dp.register_callback_query_handler(adding_case_path, text=['go_to_out_case', 'add_case'], state=FsmSelectCase)
    dp.register_callback_query_handler(check_trade_sell_case, text='check_trade', state=FsmSelectCase)
    dp.register_message_handler(set_name_steam_sell_case, state=FsmSelectCase.name_steam)
    dp.register_message_handler(set_message_by_user_sell_case, state=FsmSelectCase.other_data_for_offer)
