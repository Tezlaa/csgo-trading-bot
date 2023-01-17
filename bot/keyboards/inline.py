from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
    
"""--------------Top up balance steam---------------"""
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
    InlineKeyboardButton('Qiwi', callback_data='qiwi'),
)


def qiwi_menu(is_url=True, url="", bill="") -> InlineKeyboardMarkup:
    qiwi_kb = InlineKeyboardMarkup(row_width=1)
    if is_url:
        url_qiwi = InlineKeyboardButton('Ссылка на оплату', url=url)
        qiwi_kb.insert(url_qiwi)
        
    check_qiwi = InlineKeyboardButton('Проверить оплату', callback_data='check_' + str(bill))
    qiwi_kb.insert(check_qiwi)
    return qiwi_kb


"""--------------------Balance out------------------"""
balance_out_start = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Я хочу продать кейсы", callback_data="want_sell"),
    InlineKeyboardButton("Я хочу вывести баланс из Steam", callback_data="want_balance_out_from_steam"),
)

wont_to_balance_out_on_steam = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Вывести ключ(и)", callback_data='out_key'),
    InlineKeyboardButton("Назад", callback_data='cancel_trade'),
)

check_on_trade = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Проверить", callback_data='check_trade'),
    InlineKeyboardButton("Отмена", callback_data="cancel_trade"),
)

go_to_balance_out_start = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Вернуться в меню", callback_data="cancel_trade"),
)

sell_case_start = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Выбрать кейсы", callback_data='select_case'),
)

select_path_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("Вывести", callback_data="go_to_out_case"),
    InlineKeyboardButton("Добавить кейсы", callback_data='add_case'),
)

check_on_trade_sell_case = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Проверить", callback_data='check_trade'),
    InlineKeyboardButton("Главное меню", callback_data="go_to_menu"),
)


def count_case():
    number_case = InlineKeyboardMarkup(row_width=8)
    for number in range(1, 16):
        number_case.insert(InlineKeyboardButton(number, callback_data='count_' + str(number)))
    
    return number_case


def get_case_inline_kb(case: dict) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    
    for name in case.keys():
        keyboard.add(InlineKeyboardButton(f'«{name}»', callback_data='case_' + name))
    
    return keyboard
    

"""---------------------Top up balance bot-------------------"""
select_way_of_payment_bot = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("QIWI", callback_data='qiwi'),
    InlineKeyboardButton("Другое", callback_data='other_way_of_payment'),
)

info_about_buy = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Перейти к оплате", callback_data='go_to_payment'),
    InlineKeyboardButton("Перевести вручную", callback_data='payment_of_manually'),
)