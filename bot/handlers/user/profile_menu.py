import random
from datetime import datetime, timedelta

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import main
from bank import bank
from bot.database.sqlite_db import count_ref, get_all_top_up, get_balance_user
from bot.handlers.user.different import check_cheque, send_message_all_admin
from bot.keyboards import inline
from bot.keyboards.reply import back_kb, menu_profile, start_kb

from glQiwiApi.qiwi.clients.p2p.types import Bill


class FsmTopUpBot(StatesGroup):
    set_amount = State()
    cheque = State()


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
    name_bot = (await main.bot.get_me()).username
    await msg.answer(f"Вы получаете 3% с пополнения по вашей реферальной ссылке\n\n"
                     f"Приглашайте друзей и зарабатывайте, распространяя свою персональную ссылку:\n"
                     f"<em>https://t.me/{name_bot}?start={msg.from_user.id}\n\n</em>"
                     f'Количество ваших рефералов: <b>{await count_ref(msg.from_user.id)}</b>')


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
    except Exception:
        await msg.answer("Введите число!\n"
                         "Введите сумму, которую вы хотите пополнить на баланс")
        return

    await msg.answer("Выберите наиболее удобный для вас способ оплаты: ",
                     reply_markup=inline.select_way_of_payment_bot)


async def other(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Выберите способ оплаты:", reply_markup=inline.other)


async def other_way_of_payment(call: types.CallbackQuery, state: FSMContext):
    payment = call.data.split("_")[1]
    
    async with state.proxy() as data:
        data["payment"] = payment
    
    if payment == "sberbank":
        await call.message.edit_text(f'Отправьте деньги на СберБанк\n\n'
                                     f'Номер кошелька:\n{bank["sberbank"]["walet"]["number"]}\n\n'
                                     f'На карту:\n{bank["sberbank"]["walet"]["number_bank"]}\n\n'
                                     f'   {bank["sberbank"]["walet"]["name"]}\n'
                                     f'После оплаты отправьте скриншот')
        return await FsmTopUpBot.next()
        
    elif payment == "tinkoff":
        await call.message.edit_text(f'Отправьте деньги на Тинькоф\n\n'
                                     f'На карту:\n{bank["sberbank"]["walet"]["number_bank"]}\n\n'
                                     f'   {bank["sberbank"]["walet"]["name"]}\n'
                                     f'После оплаты отправьте скриншот')
        return await FsmTopUpBot.next()
        
    elif payment == "youmoney":
        await call.message.edit_text(f'Отправьте деньги на Юмани\n\n'
                                     f'На карту:\n{bank["sberbank"]["walet"]["number_bank"]}\n\n'
                                     f'После оплаты отправьте скриншот')
        return await FsmTopUpBot.next()
        
    elif payment == "yota":
        await call.message.edit_text(f'Отправьте деньги на Yola\n\n'
                                     f'Номер кошелька:\n{bank["sberbank"]["walet"]["number"]}\n\n'
                                     f'Комиссия при пополнении баланса через Yota 10%!\n'
                                     f'После оплаты отправьте скриншот')
        return await FsmTopUpBot.next()


async def top_up_balance_bot_via_qiwi(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        await call.message.edit_text(f'Теперь осталось оплатить счёт на {data["amount"]}руб\n'
                                     f'После оплаты бот автоматически зачислит сумму на ваш баланс.',
                                     reply_markup=inline.info_about_buy)

        
async def top_up_balance_bot_via_qiwi_manually(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["payment"] = "qiwi"
        await call.message.edit_text(f'Отправьте {data["amount"]} на Qiwi:\n'
                                     f'Номер кошелька: `+79173670708`\n'
                                     f'После оплаты отправьте нам скриншот чека',
                                     parse_mode='MARKDOWN')
    
    await FsmTopUpBot.next()


async def set_cheque(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["cheque"] = msg.photo[-1].file_id
        
    username = msg.from_user.username if msg.from_user.username != "None" else msg.from_user.first_name
    
    text_for_admin = (f'_❗Пополнение_\n'
                      f'User: `{username}`\n'
                      f'Через {data["payment"]} на ***{data["amount"]}руб***\n'
                      f'Чек пользователя: ')
    await send_message_all_admin(text_for_admin)
    await check_cheque(data["cheque"], data["amount"], msg.from_user.id)
    await msg.answer('Заявка подана, ждите пополнения, проверка занимает до 24 часов',
                     reply_markup=start_kb)
    
    await state.finish()
    

async def go_to_payment_via_qiwi(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        pass
    comment = str(call.from_user.id) + "_" + str(random.randint(10000, 99999))
        
    bill = await main.p2p_qiwi.create_p2p_bill(amount=data['amount'],
                                               expire_at=(datetime.now() + timedelta(minutes=3)),
                                               comment=comment)
    async with state.proxy() as data:
        data["bill"] = bill
        data["payment"] = "qiwi"
    
    await call.message.edit_text(f'Отправьте <b>{data["amount"]}</b>руб на счёт QIWI\n'
                                 f'Указав в комментарии к оплате: <b>{comment}</b>\n'
                                 f'<a href="{bill.pay_url}">ССЫЛКА</a>',
                                 reply_markup=inline.qiwi_menu(url=bill.pay_url, bill=bill.id),
                                 parse_mode="HTML")


async def check_on_payment(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        bill: Bill = data.get("bill")
    
    if await main.p2p_qiwi.check_if_bill_was_paid(bill):
        
        username = call.from_user.username if call.from_user.username != "None" else call.from_user.first_name
                    
        text_for_admin = (f'_❗Пополнение_\n'
                          f'User: `{username}`\n'
                          f'Через {data["payment"]} на ***{data["amount"]}руб***')
        
        await send_message_all_admin(text_for_admin)
        await call.message.edit_text('Пополение успешно', reply_markup=start_kb)
        
        await state.finish()
    else:
        await call.message.answer('Вы не оплатили счёт', reply_markup=inline.qiwi_menu(is_url=False, bill=bill.id))
        
        
def register_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(get_profile, Text(equals='Профиль'))
    dp.register_message_handler(referal_sistem, Text(equals='Реферальная система'))
    dp.register_message_handler(top_up_balance_bot, Text(equals='Пополнить баланс'))
    dp.register_message_handler(set_how_much_top_up, state=FsmTopUpBot.set_amount)
    dp.register_callback_query_handler(other, text_contains="other_way_of_payment", state=FsmTopUpBot)
    dp.register_callback_query_handler(other_way_of_payment, text_contains="payment_", state=FsmTopUpBot)
    dp.register_callback_query_handler(top_up_balance_bot_via_qiwi, text='qiwi', state=FsmTopUpBot)
    dp.register_callback_query_handler(top_up_balance_bot_via_qiwi_manually, text='payment_of_manually',
                                       state=FsmTopUpBot)
    dp.register_message_handler(set_cheque, content_types=["photo"], state=FsmTopUpBot.cheque)
    dp.register_callback_query_handler(go_to_payment_via_qiwi, text='go_to_payment', state=FsmTopUpBot)
    dp.register_callback_query_handler(check_on_payment, text_contains="check_", state=FsmTopUpBot)