from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, \
    KeyboardButton

"""--------------Top up balance steam---------------"""
top_up_balance_steam = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🔓Открыта", callback_data='open_market'),
    InlineKeyboardButton('🔒Закрыта', callback_data='close_market'),
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
    InlineKeyboardButton('🤖Баланс бота', callback_data='bot'),
    InlineKeyboardButton('Qiwi', callback_data='qiwi'),
)


def offer_steam(user_id: str, msg_id: list):
    kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("✅Пополнено",
                             callback_data=f"topupsteam_agree_{user_id}_{msg_id}"),
        InlineKeyboardButton("❌Не пополнено",
                             callback_data=f"topupsteam_notagree_{user_id}_{msg_id}"),
    )
    return kb


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
    InlineKeyboardButton("💵Я хочу продать кейсы", callback_data="want_sell"),
    InlineKeyboardButton("💳Я хочу вывести баланс из Steam", callback_data="want_balance_out_from_steam"),
)

wont_to_balance_out_on_steam = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🔑Вывести ключ(и)", callback_data='out_key'),
    InlineKeyboardButton("⏪Назад", callback_data='cancel_trade'),
)

check_on_trade = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🔎Проверить", callback_data='check_trade'),
    InlineKeyboardButton("⛔Отмена", callback_data="cancel_trade"),
)

go_to_balance_out_start = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Вернуться в меню", callback_data="cancel_trade"),
)

sell_case_start = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("➕Выбрать кейсы", callback_data='select_case'),
)

select_path_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("💵Вывести", callback_data="go_to_out_case"),
    InlineKeyboardButton("➕Добавить кейсы", callback_data='add_case'),
)

check_on_trade_sell_case = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🔎Проверить", callback_data='check_trade'),
    InlineKeyboardButton("Главное меню", callback_data="go_to_menu"),
)


def count_case():
    number_case = InlineKeyboardMarkup(row_width=8)
    for number in range(1, 16):
        number_case.insert(InlineKeyboardButton(str(number), callback_data='count_' + str(number)))
    
    return number_case


def get_case_inline_kb(case: dict, how_much_case=9) -> InlineKeyboardMarkup:
    if how_much_case == 0:
        how_much_case = 10 * 10
    
    keyboard = InlineKeyboardMarkup(row_width=2)
    len_case = len(case)
    
    for index, name in enumerate(case.keys()):
        keyboard.insert(InlineKeyboardButton(f'«{name}»', callback_data='case_' + name))
        if how_much_case == index:
            last_case = [name, index]
            break
    
    try:
        if last_case[1] != len_case:
            keyboard.add(InlineKeyboardButton('↪Другие кейсы', callback_data='case_all'))
    except Exception:
        pass
        
    return keyboard
    

"""---------------------------Profile--------------------------"""
select_way_of_payment_bot = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("QIWI", callback_data='qiwi'),
    InlineKeyboardButton("💳Другое", callback_data='other_way_of_payment'),
)

info_about_buy = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("💳Перейти к оплате", callback_data='go_to_payment'),
    InlineKeyboardButton("💪Перевести вручную", callback_data='manually'),
)


other = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("Сбербанк", callback_data='payment_sberbank'),
    InlineKeyboardButton("Тинькофф", callback_data='payment_tinkoff'),
    InlineKeyboardButton("Юмани", callback_data='payment_youmoney'),
    InlineKeyboardButton("Yota", callback_data='payment_yota'),
)


def check_cheque_admin(how_much: str, id_user: str, message_id: str):
    check_cheque_admin_kb = InlineKeyboardMarkup(row_width=1).add(
        InlineKeyboardButton("Чек в порядке, зачислить на баланс " + how_much + "руб",
                             callback_data=f'GoodCheque_{id_user}_{how_much}_{message_id}'),
        InlineKeyboardButton("Отмена", callback_data=f'NotOkCheque_{id_user}_{how_much}_{message_id}'),
    )
    return check_cheque_admin_kb


"""---------------------------Trade case-----------------------"""
select_path_trade_case_kb = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🔫Выбрать скины", callback_data="go_to_add_skins"),
    InlineKeyboardButton("🧰Добавить кейсы", callback_data='add_case'),
)

agree_or_no = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("✅Подтвердить", callback_data="agree"),
    InlineKeyboardButton("⛔Отменить", callback_data="not_agree"),
)

before_adding_skin = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("➕Добавить скины", callback_data="go_to_add_skins"),
    InlineKeyboardButton("🚀Перейти к обмену", callback_data="go_to_trade"),
)

no_money_for_add_skin = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🚀Перейти к обмену", callback_data="go_to_trade"),
    InlineKeyboardButton("➕Добавить кейсы", callback_data='add_case'),
)


def select_skin_kb(how_much_price_case: str, all_skin_for_trade: dict, how_much_skin=10):
    if how_much_skin == 0:
        how_much_skin = 10 * 10
    
    skin_kb = InlineKeyboardMarkup(row_width=2)
    len_skin = len(all_skin_for_trade)
    
    index = 1
    for skin, price in all_skin_for_trade.items():
        if price < how_much_price_case:
            skin_kb.insert(
                KeyboardButton(skin, callback_data=f'skin_{skin}'),
            )
            if how_much_skin == index:
                last_skin = [skin, index]
                break
            index += 1
        
    if len(skin_kb.inline_keyboard) == 0:
        raise ZeroDivisionError
    
    try:
        if last_skin[1] != len_skin:
            skin_kb.add(InlineKeyboardButton('↪Другие скрины', callback_data='skin_all'))
    except Exception:
        pass
    
    skin_kb.add(InlineKeyboardButton("🧰Добавить кейс", callback_data="add_case"))
    
    return skin_kb


"""------------------------------Rules-------------------------"""

select_rules = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🏹Требования к аккаунту", callback_data="requirements"),
    InlineKeyboardButton("❓Где взять логин", callback_data="where_to_get"),
    InlineKeyboardButton("💵Лимиты на пополнение", callback_data="limit_on_payment"),
    InlineKeyboardButton("💢Не пришли деньги на баланс", callback_data="no_money_came_in"),
    InlineKeyboardButton("📉Пришла сумма меньше", callback_data="came_in_money_less"),
    InlineKeyboardButton("💰Как я получу свой баланс в steam?", callback_data="how_get_balance_steam"),
    InlineKeyboardButton("🛡Политика возврата", callback_data="return_policy"),
)

go_to_back_by_rules = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("⏪Назад", callback_data="go_to_back"),
)

"""------------------------------Game---------------------------"""

game_menu = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("✂Камень-ножницы-бумага", callback_data="stone_scissor_paper"),
    InlineKeyboardButton("🐦Попади в птицу", callback_data="kill_bird"),
    InlineKeyboardButton("🦅Орёл и решка", callback_data="eagle_and_tails"),
)

# stone_scissor_paper
menu_ssp = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🚀Перейти к игре", callback_data="go_to_play_ssp"),
    InlineKeyboardButton("⏪Вернуться назад", callback_data="go_to_game_menu"),
)

choice_kb = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🗿Камень", callback_data="choicessp_stone"),
    InlineKeyboardButton("✂Ножницы", callback_data="choicessp_scissor"),
    InlineKeyboardButton("📜Бумага", callback_data="choicessp_paper"),
)

win_ssp = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🤑Играть снова", callback_data="play_again_ssp"),
    InlineKeyboardButton("Забрать", callback_data="take_win"),
)

lose_ssp = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🤑Играть снова", callback_data="go_to_play_ssp"),
    InlineKeyboardButton("⏪Выбрать другую игру", callback_data="go_to_game_menu"),
)

# kill bird
menu_kbg = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🚀Перейти к игре", callback_data="go_to_play_kbg"),
    InlineKeyboardButton("⏪Вернуться назад", callback_data="go_to_game_menu"),
)

choice_kbg_kb = InlineKeyboardMarkup(row_width=2)
up = InlineKeyboardButton("⬆", callback_data="choicekbg_up")
left = InlineKeyboardButton("⬅", callback_data="choicekbg_left")
right = InlineKeyboardButton("➡", callback_data="choicekbg_right")
choice_kbg_kb.insert(up)
choice_kbg_kb.add(left)
choice_kbg_kb.insert(right)

win_kbg = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🤑Играть дальше", callback_data="play_again_kbg"),
    InlineKeyboardButton("Забрать", callback_data="take_win"),
)

lose_kbg = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("💵Играть снова", callback_data="go_to_play_kbg"),
    InlineKeyboardButton("⏪Выбрать другую игру", callback_data="go_to_game_menu"),
)

# eagle_and_tails
menu_eat = InlineKeyboardMarkup(row_width=2).add(
    InlineKeyboardButton("🚀Перейти к игре", callback_data="go_to_play_eat"),
    InlineKeyboardButton("⏪Вернуться назад", callback_data="go_to_game_menu"),
)

choice_eat = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🦅Орёл", callback_data="choiceeat_eagle"),
    InlineKeyboardButton("🪙Решка", callback_data="choiceeat_tails"),
)

result_eat = InlineKeyboardMarkup(row_width=1).add(
    InlineKeyboardButton("🤑Играть снова", callback_data="play_again_eat"),
    InlineKeyboardButton("⏪Выбрать другую игру", callback_data="go_to_game_menu"),
)