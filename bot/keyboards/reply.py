from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


"""START MENU"""
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Пополнить баланс steam")).add(
    KeyboardButton("Вывести баланс"), KeyboardButton("Обменять кейсы")).add(
    KeyboardButton("Мини игры"), KeyboardButton("Профиль"), KeyboardButton("Правила")).add(
    KeyboardButton("Соц сети"))

"""menu: TOP UP BALANCE STEAME"""
select_type_market_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton('Где взять трейд-ссылку?'),
    KeyboardButton('Главное меню'),
)

go_to_main_menu = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton('Главное меню'),
)

"""menu: BALANCE OUT"""
wont_to_balance_out_on_steam = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton("Вывести ключ(и)"),
    KeyboardButton("Назад"),
)

back_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton('Главное меню'),
    KeyboardButton("Назад"),
)

"""menu: Profile"""
menu_profile = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton("Реферальная система"),
    KeyboardButton("Пополнить баланс"),
    KeyboardButton("Главное меню"),
)
"""menu: Game"""
game_main_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton("Главное меню"),
    KeyboardButton("Выбрать другую игру"),
)