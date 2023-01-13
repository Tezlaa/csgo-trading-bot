from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
    
start_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(
    KeyboardButton("Пополнить баланс steam")).add(
    KeyboardButton("Вывести баланс"), KeyboardButton("Обменять кейсы")).add(
    KeyboardButton("Мини игры"), KeyboardButton("Профиль"), KeyboardButton("Правила")).add(
    KeyboardButton("Соц сети"))