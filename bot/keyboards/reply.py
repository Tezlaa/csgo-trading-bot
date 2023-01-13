from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove


"""START MENU"""
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Пополнить баланс steam")).add(
    KeyboardButton("Вывести баланс"), KeyboardButton("Обменять кейсы")).add(
    KeyboardButton("Мини игры"), KeyboardButton("Профиль"), KeyboardButton("Правила")).add(
    KeyboardButton("Соц сети"))

"""menu: TOP UP BALANCE STEAME"""
open_market_kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    KeyboardButton('Где взять трейд взять ссылку?'),
    KeyboardButton('Главное меню')
)