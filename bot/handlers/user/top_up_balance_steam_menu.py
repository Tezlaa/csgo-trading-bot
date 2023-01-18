
import random
from datetime import datetime, timedelta

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


class FsmMarket(StatesGroup):
    set_trade_link = State()
    set_login = State()
    set_amount = State()
    select_payment = State()
    payment_p2p = State()


async def top_up_steam(msg: types.Message):
    await msg.answer('От вашего выбора зависит курс пополнения.\n У вас открыта торговая площадка?',
                     reply_markup=inline.top_up_balance_steam)

         
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
                                     f'Указав в комментарии к оплате: {comment}\n'
                                     f'<a href="{bill.pay_url}">ССЫЛКА</a>',
                                     reply_markup=inline.qiwi_menu(url=bill.pay_url, bill=bill.id),
                                     parse_mode="HTML")
        
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


def register_top_up_balance_steam_handlers(dp: Dispatcher):
    dp.register_message_handler(top_up_steam, Text(equals='Пополнить баланс steam'))

    dp.register_callback_query_handler(open_market, text='open_market')
    dp.register_callback_query_handler(close_market, text='close_market')
    dp.register_message_handler(set_link, state=FsmMarket.set_trade_link)
    dp.register_message_handler(set_user_login, state=FsmMarket.set_login)
    dp.register_callback_query_handler(set_amount, state=FsmMarket.set_amount)
    dp.register_message_handler(set_amount, state=FsmMarket.set_amount)
    dp.register_callback_query_handler(select_payment, state=FsmMarket.select_payment)
    dp.register_callback_query_handler(qiwi_payment, text_contains="check_", state=FsmMarket.payment_p2p)