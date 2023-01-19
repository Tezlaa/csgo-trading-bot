from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from bot.keyboards.reply import start_kb


async def go_to_menu(msg: (types.Message or types.CallbackQuery), state: FSMContext):  # for exit
    await state.finish()
    if type(msg) == types.CallbackQuery:
        msg = msg.message
    await msg.answer("Главное меню", reply_markup=start_kb)


def register_user_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(go_to_menu, text=["go_to_menu", "cancel_trade"], state="*")  # for exit
    dp.register_message_handler(go_to_menu, Text(equals="Главное меню"), state="*")  # for exit
