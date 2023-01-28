from aiogram import Dispatcher, types

from bot import main
from bot.database.sqlite_db import get_admin_id, top_up_balance, get_all_user, set_active, get_all_active
from bot.handlers.user.different import delete_cheque


async def send_msg_all_user(msg: types.Message):
    text = msg.text[9:]
    if str(msg.from_user.id) in await get_admin_id():
        for user_id in await get_all_user():
            try:
                await main.bot.send_message(user_id[0], text)
                await set_active(user_id[0], 1)
            except Exception:
                await set_active(user_id[0], 0)
        await msg.answer("Рассылка успешно выполнена")
    return


async def get_stat(msg: types.Message):
    if str(msg.from_user.id) in await get_admin_id():
        all_user = len(await get_all_user())
        active_user = len(await get_all_active())
        delete_user = all_user - active_user
        admins = len(await get_admin_id())
        
        await msg.answer(f"▪️Пользователей: {all_user}\n"
                         f"▫️Активных: {active_user}\n"
                         f"▫️Удаленных: {delete_user}\n"
                         f"▪️Админов: {admins}")
                   
            
async def top_up_balance_steam(call: types.CallbackQuery):
    data_kb = call.data.split("_")
    user_id = data_kb[2]
    msg_id = data_kb[3]
    how_much = data_kb[4]
    isbot = data_kb[5]

    if data_kb[1] == "agree":
        await main.bot.send_message(user_id, text="💎Ваш баланс успешно пополнен!")
        for admin_id in await get_admin_id():
            await delete_cheque(admin_id, msg_id, text="Пополнено!✅")
    elif data_kb[1] == "notagree":
        if isbot == "+":
            await main.bot.send_message(user_id, "❗Не было зачислено на баланс Steam\n"
                                                 "Выполнен возврат на баланс")
            await top_up_balance(how_much, user_id)
        else:
            await main.bot.send_message(user_id, "❗Не было зачислено на баланс Steam\n")
        for admin_id in await get_admin_id():
            await delete_cheque(admin_id, msg_id, text="Не пополнено!❌")


async def check_is_good(call: types.CallbackQuery):
    data = call.data.split("_")
    id_user = data[1]
    how_much = data[2]
    msg_id = data[3]
    
    await top_up_balance(how_much, id_user)
    for admin_id in await get_admin_id():
        await delete_cheque(admin_id, msg_id, text="Подтверждена!✅")
        
    await main.bot.send_message(id_user, f"💎Вам зачислено <b>{how_much}руб</b> на баланс")
    

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
    dp.register_message_handler(get_stat, commands=['statistic'])
    dp.register_message_handler(send_msg_all_user, commands=['sendAll'])
    dp.register_callback_query_handler(top_up_balance_steam, text_contains='topupsteam_')
    
    dp.register_callback_query_handler(check_is_good, text_contains='GoodCheque_')
    dp.register_callback_query_handler(check_is_not_ok, text_contains='NotOkCheque_')