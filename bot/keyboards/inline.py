from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
    

top_up_balance_steam = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Открыта", callback_data='open_market'),
    InlineKeyboardButton('Закрыта', callback_data='close_market'),
)

button_price = InlineKeyboardMarkup(row_width=3).add(
    InlineKeyboardButton("100руб", callback_data='100'),
    InlineKeyboardButton("300руб", callback_data='300'),
    InlineKeyboardButton("500руб", callback_data='500'),
    InlineKeyboardButton("1000руб", callback_data='1000'),
    InlineKeyboardButton("3000руб", callback_data='3000'),
    InlineKeyboardButton("5000руб", callback_data='5000'),
)

way_of_payment = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton('Баланс бота', callback_data='bot'),
    InlineKeyboardButton('Qiwi', callback_data='qiwi')
)