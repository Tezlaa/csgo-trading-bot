import logging

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.keyboards.inline import top_up_balance_steam, button_price, way_of_payment
from bot.keyboards.reply import open_market_kb


class FSMselectMarket(StatesGroup):
    set_login = State()
    set_amount = State()
    select_payment = State()


async def top_up_steam(msg: types.Message):
    await msg.answer('От вашего выбора зависит курс пополнения.\n У вас открыта торговая площадка?',
                     reply_markup=top_up_balance_steam)


async def open_market(call: types.CallbackQuery):
    await call.message.answer('Для продолжения операции отправьте вашу трейд ссылку следующим сообщением',
                              reply_markup=open_market_kb)


async def close_market(call: types.CallbackQuery):
    await FSMselectMarket.set_login.set()
    await call.message.answer('Введите логин Steam.\n(Что такое логин, можно узнать во вкладке FAQ)')


async def set_user_login(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_login"] = msg.text
    await msg.answer('Введите сумму пополнения или выберите из популярных', reply_markup=button_price)
    await FSMselectMarket.next()


async def set_amount(msg, state: FSMContext):
    if type(msg) is types.CallbackQuery:
        async with state.proxy() as data:
            data["amount"] = msg.data
            msg = msg.message
    else:
        async with state.proxy() as data:
            data["amount"] = msg.text

    await msg.answer(f'Информация по оплате\n'
                     f'Логин: {data["user_login"]}\n'
                     f'Заплатите: {data["amount"]}руб\n'
                     f'Получите: {data["amount"]}руб\n\n'
                     f'Выберите способ оплаты', reply_markup=way_of_payment)
    await FSMselectMarket.next()


async def select_payment(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["payment_via"] = call.data

    await call.message.answer(f'{data["user_login"]}, {data["amount"]}, {data["payment_via"]}')
    await state.finish()


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(top_up_steam, Text(equals='Пополнить баланс steam'))
    
    dp.register_callback_query_handler(close_market, text='close_market')
    dp.register_message_handler(set_user_login, state=FSMselectMarket.set_login)
    dp.register_callback_query_handler(set_amount, state=FSMselectMarket.set_amount)
    dp.register_message_handler(set_amount, state=FSMselectMarket.set_amount)
    dp.register_callback_query_handler(select_payment, state=FSMselectMarket.select_payment)
    dp.register_callback_query_handler(open_market, text='open_market')