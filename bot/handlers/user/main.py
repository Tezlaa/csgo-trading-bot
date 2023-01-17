import logging
import os
import random
from datetime import datetime, time, timedelta

from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import main
from bot.database.sqlite_db import get_admin_id, unbalance, get_balance_user, get_all_top_up
from bot.handlers.user.different import get_all_price_case, get_case, get_text_with_all_case,\
    send_message_all_admin
from bot.keyboards import inline
from bot.keyboards.reply import back_kb, go_to_main_menu, select_type_market_kb, start_kb, menu_profile

from glQiwiApi import QiwiP2PClient
from glQiwiApi.qiwi.clients.p2p.types import Bill

import pytz


class FsmMarket(StatesGroup):
    set_trade_link = State()
    set_login = State()
    set_amount = State()
    select_payment = State()
    payment_p2p = State()


class FsmWantOutBalanceFromSteam(StatesGroup):
    name_steam = State()
    other_data_for_offer = State()


class FsmSelectCase(StatesGroup):
    witch_case = State()
    how_much = State()
    name_steam = State()
    other_data_for_offer = State()
    
    
class FsmTopUpBot(StatesGroup):
    set_amount = State()
    payment = State()


"""top up balance steam"""


async def top_up_steam(msg: types.Message):
    await msg.answer('От вашего выбора зависит курс пополнения.\n У вас открыта торговая площадка?',
                     reply_markup=inline.top_up_balance_steam)


async def go_to_menu(msg: (types.Message or types.CallbackQuery), state: FSMContext):  # for exit
    await state.finish()
    if type(msg) == types.CallbackQuery:
        msg = msg.message
    await msg.answer("Главное меню", reply_markup=start_kb)
      
         
async def open_market(call: types.CallbackQuery):
    await FsmMarket.set_trade_link.set()
    await main.bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer('Для продолжения операции отправьте вашу трейд-ссылку следующим сообщением',
                              reply_markup=select_type_market_kb)


async def close_market(call: types.CallbackQuery):
    await FsmMarket.set_login.set()
    await main.bot.delete_message(call.message.chat.id, call.message.message_id)
    await call.message.answer('Введите логин Steam.\n(Что такое логин, можно узнать во вкладке FAQ)',
                              reply_markup=go_to_main_menu)


async def set_link(msg: types.Message, state: FSMContext):
    if msg.text == "Где взять трейд-ссылку?":
        await msg.answer("https://www.youtube.com/watch?v=w3-eDOaOjx8")
        await msg.answer('Для продолжения операции отправьте вашу трейд-ссылку следующим сообщением',
                         reply_markup=go_to_main_menu)
        return
    elif msg.text.find("https://steamcommunity.com/tradeoffer/new/") == 0:
        async with state.proxy() as data:
            data["user_link"] = msg.text
        await FsmMarket.next()
        await FsmMarket.next()
        await msg.answer('Введите сумму пополнения или выберите из популярных',
                         reply_markup=inline.button_price)
    else:
        await msg.answer("Неправильная трейд-ссылка!\nОтправьте ссылку в правильном формате",
                         reply_markup=select_type_market_kb)
        return
        

async def set_user_login(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_login"] = msg.text
    await msg.answer('Введите сумму пополнения или выберите из популярных',
                     reply_markup=inline.button_price)
    await FsmMarket.next()


async def set_amount(msg, state: FSMContext):
    if type(msg) is types.CallbackQuery:
        async with state.proxy() as data:
            data["amount"] = msg.data
            msg = msg.message
    else:
        if int(msg.text) > 100:
            async with state.proxy() as data:
                data["amount"] = msg.text
        else:
            await msg.answer('Минимальная сумма - 100руб\nВведите сумму пополнения или выберите из популярных',
                             reply_markup=inline.button_price)
            return
    
    async with state.proxy() as data:
        try:
            data["link_or_login"] = f'Логин: {data["user_login"]}'
        except KeyError:
            data["link_or_login"] = f'Трейд-ссылка: <a href="{data["user_link"]}">ССЫЛКА</a>'
    await main.bot.delete_message(msg.chat.id, msg.message_id)
    await main.bot.send_message(msg.chat.id,
                                text=f'Информация по оплате\n\n'
                                     f'{data["link_or_login"]}\n'
                                     f'Заплатите: {data["amount"]}руб\n'
                                     f'Получите: {data["amount"]}руб\n\n'
                                     f'Выберите способ оплаты',
                                reply_markup=inline.way_of_payment,
                                disable_web_page_preview=True)
    await FsmMarket.next()


async def select_payment(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["payment_via"] = call.data
    
    if data["payment_via"] == 'bot':
        try:
            await unbalance(data['amount'], call.from_user.id)
        except ValueError:  # if not enough balance
            await call.message.edit_text('Недостаточно денег на балансе бота!\n'
                                         'Введите сумму пополнения или выберите из популярных',
                                         reply_markup=inline.button_price)
            return await FsmMarket.previous()
        
        await state.finish()
        await call.message.answer("Заявка подана, ждите пополнения",
                                  reply_markup=start_kb)
        
        # send all admin
        if data["link_or_login"][:5] == "Трейд":
            login_or_link = data["link_or_login"].split(" ")[1]
        else:
            login_or_link = data["link_or_login"].split(" ")[1]
        
        text_for_admin = (f"_❗Заявка на пополнение_\n"
                          f"Пополнение: `{login_or_link}`\n"
                          f"Через {data['payment_via']} на ***{data['amount']}руб***")
            
        await send_message_all_admin(text_for_admin)
            
    elif data["payment_via"] == 'qiwi':
        comment = str(call.from_user.id) + "_" + str(random.randint(10000, 99999))
        
        bill = await main.p2p_qiwi.create_p2p_bill(amount=data['amount'],
                                                   expire_at=(datetime.now() + timedelta(minutes=3)),
                                                   comment=comment)
        async with state.proxy() as data:
            data["bill"] = bill
        
        await call.message.edit_text(f'Отправьте {data["amount"]}руб на счёт QIWI\n'
                                     f'Ссылка: {bill.pay_url}\n'
                                     f'Указав в комментарии к оплате: {comment}',
                                     reply_markup=inline.qiwi_menu(url=bill.pay_url, bill=bill.id))
        
        await FsmMarket.next()


async def qiwi_payment(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        bill: Bill = data.get("bill")
    
    if await main.p2p_qiwi.check_if_bill_was_paid(bill):
        
        async with state.proxy() as data:
            if data["link_or_login"][:5] == "Трейд":
                login_or_link = data["link_or_login"][:5].split('"')[1]
            else:
                login_or_link = data["link_or_login"][:5].split(" ")[1]
            
            text_for_admin = (f"_❗Заявка на пополнение_\n"
                              f"Пополнение: `{login_or_link}`\n"
                              f"Через {data['amount']} на ***{data['payment_via']}руб***")
            
            await send_message_all_admin(text_for_admin)
            
        await call.message.edit_caption('Ожидайте поступления средств',
                                        reply_markup=start_kb)
        await state.finish()
    else:
        await call.message.answer('Вы не оплатили счёт', reply_markup=inline.qiwi_menu(is_url=False, bill=bill.id))


"""balance out"""


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
                                 'За каждый ключ вы получите 112Р.', reply_markup=inline.wont_to_balance_out_on_steam)


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
    
    username = msg.from_user.username
    if username == "None":
        username = msg.from_user.first_name
    
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
    
    username = msg.from_user.username
    if username == "None":
        username = msg.from_user.first_name
        
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


"""Profile"""
async def get_profile(msg: types.Message):
    if type(msg) == types.CallbackQuery:
        msg = msg.message
    elif msg.text != "Назад":
        await msg.answer("Профиль", reply_markup=back_kb)
    
    user_id = msg.from_user.id
    await msg.answer(f'id: {user_id}\n'
                     f'Баланс: {await get_balance_user(user_id)}руб\n'
                     f'Всего пополнено: {await get_all_top_up(user_id)}руб', reply_markup=menu_profile)


async def referal_sistem(msg: types.Message):
    pass


async def top_up_balance_bot(msg: types.Message):
    await FsmTopUpBot.set_amount.set()
    await msg.answer("Введите сумму, которую вы хотите пополнить на баланс")


async def set_how_much_top_up(msg: types.Message, state: FSMContext):
    try:
        if int(msg.text) > 0:
            async with state.proxy() as data:
                data["amount"] = msg.text
        else:
            await msg.answer("Введите число больше нуля\n"
                             "Введите сумму, которую вы хотите пополнить на баланс")
            return
    except Exception:  # need check
        await msg.answer("Введите число!\n"
                         "Введите сумму, которую вы хотите пополнить на баланс")
        return

    await msg.answer("Выберите наиболее удобный для вас способ оплаты: ",
                     reply_markup=inline.select_way_of_payment_bot)
    await FsmTopUpBot.next()


async def top_up_balance_bot_via_qiwi(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await call.message.answer(f'Теперь осталось оплатить счёт на {data["amount"]}руб\n'
                                  f'После оплаты бот автоматически зачислит сумму на ваш баланс.',
                                  reply_markup=inline.info_about_buy) 


def register_user_handlers(dp: Dispatcher):
    """top up balance steam"""
    dp.register_message_handler(top_up_steam, Text(equals='Пополнить баланс steam'))
    
    dp.register_callback_query_handler(go_to_menu, text="go_to_menu", state="*")  # for exit
    dp.register_message_handler(go_to_menu, Text(equals="Главное меню"), state="*")  # for exit
    dp.register_callback_query_handler(open_market, text='open_market')
    dp.register_callback_query_handler(close_market, text='close_market')
    dp.register_message_handler(set_link, state=FsmMarket.set_trade_link)
    dp.register_message_handler(set_user_login, state=FsmMarket.set_login)
    dp.register_callback_query_handler(set_amount, state=FsmMarket.set_amount)
    dp.register_message_handler(set_amount, state=FsmMarket.set_amount)
    dp.register_callback_query_handler(select_payment, state=FsmMarket.select_payment)
    dp.register_callback_query_handler(qiwi_payment, text_contains="check_", state=FsmMarket.payment_p2p)
    
    """balance out"""
    dp.register_callback_query_handler(balance_out, text=['cancel_trade'], state="*")
    dp.register_message_handler(balance_out, Text(equals=['Вывести баланс', 'Назад']))
    
    dp.register_callback_query_handler(balance_out_from_steam, text="want_balance_out_from_steam")
    dp.register_callback_query_handler(out_key, text='out_key')
    dp.register_callback_query_handler(check_user_on_trade, text='check_trade')
    dp.register_message_handler(set_name_steam,
                                state=FsmWantOutBalanceFromSteam.name_steam)
    dp.register_message_handler(set_message_by_user,
                                state=FsmWantOutBalanceFromSteam.other_data_for_offer)
    dp.register_callback_query_handler(sell_case, text='want_sell')
    dp.register_callback_query_handler(set_case, text='select_case', state=FsmSelectCase)
    dp.register_callback_query_handler(set_how_case, text_contains='case_', state=FsmSelectCase.witch_case)
    dp.register_callback_query_handler(info_about_adding, text_contains="count_", state=FsmSelectCase.how_much)
    dp.register_callback_query_handler(adding_case_path, text=['go_to_out_case', 'add_case'], state=FsmSelectCase)
    dp.register_callback_query_handler(check_trade_sell_case, text='check_trade', state=FsmSelectCase)
    dp.register_message_handler(set_name_steam_sell_case,
                                state=FsmSelectCase.name_steam)
    dp.register_message_handler(set_message_by_user_sell_case,
                                state=FsmSelectCase.other_data_for_offer)
    """profile"""
    dp.register_message_handler(get_profile, Text(equals='Профиль'))
    dp.register_message_handler(referal_sistem, Text(equals='Реферальная система'))
    dp.register_message_handler(top_up_balance_bot, Text(equals='Пополнить баланс'))
    dp.register_message_handler(set_how_much_top_up, state=FsmTopUpBot.set_amount)
    dp