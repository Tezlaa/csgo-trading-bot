from aiogram import Dispatcher, types

from bot import main
from bot.database.sqlite_db import get_admin_id, top_up_balance
from bot.handlers.user.different import delete_cheque


async def check_is_good(call: types.CallbackQuery):
    data = call.data.split("_")
    id_user = data[1]
    how_much = data[2]
    msg_id = data[3]
    
    await top_up_balance(how_much, id_user)
    for admin_id in await get_admin_id():
        await delete_cheque(admin_id, msg_id, text="Подтверждена!✅")
        
    await main.bot.send_message(id_user, f"Вам зачислено {how_much}руб на баланс")
    

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