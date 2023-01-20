import random

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.keyboards.inline import game_menu, menu_ssp, choice_kb, win_ssp, lose_ssp, menu_kbg, choice_kbg_kb, win_kbg,\
    lose_kbg
from bot.keyboards.reply import game_main_kb, start_kb
from bot.database.sqlite_db import get_balance_user, set_balance, unbalance


class FsmSSP(StatesGroup):
    ssp_game = State()
    set_bet_to_game = State()
    choice_user = State()
    
    select_path = State()


class FsmKBG(StatesGroup):
    kill_bird_game = State()
    set_bet_to_game = State()
    choice_user = State()
    
    select_path = State()
    

async def go_to_menu(msg: (types.Message or types.CallbackQuery), state: FSMContext):
    await state.finish()
    if type(msg) == types.CallbackQuery:
        msg.answer = msg.message.edit_text
    else:
        await msg.answer("🎮Мини игры", reply_markup=game_main_kb)

    await msg.answer("Выберете игру:", reply_markup=game_menu)


async def ssp_info(call: types.CallbackQuery):
    await call.message.edit_text("✂Игра 'Камень-Ножницы-Бумага'\n\n"
                                 "<em>Победитель определяется по правилам:\n"
                                 "— камень побеждает ножницы (камень затупляет ножницы)\n"
                                 "— ножницы побеждают бумагу (ножницы разрезают бумагу)\n"
                                 "— бумага побеждает камень (бумага заворачивает камень)\n"
                                 "— ничья, если показан одинаковый знак</em>\n",
                                 reply_markup=menu_ssp)
    await FsmSSP.ssp_game.set()
    

async def play_ssp_menu(call: types.CallbackQuery, state: FSMContext):
    global min_rate
    balance = await get_balance_user(call.from_user.id)
    
    min_rate = 10  # minimum bet to play
    
    if balance > min_rate:
        await call.message.edit_text(f'У вас на счету: {await get_balance_user(call.from_user.id)} руб\n'
                                     f'Минимальная ставка: {min_rate} руб\n'
                                     f'Выиграш +30% к вашей ставке\n\n'
                                     f'🚀<b>Отправьте вашу ставку:</b>')
        await FsmSSP.next()
    else:
        await call.message.edit_text("Недостаточно баланса")
        await call.message.delete()
        
        await call.message.answer(f'💢У вас на счету: {await get_balance_user(call.from_user.id)}руб\n'
                                  f'Минимальная ставка: {min_rate} руб\n\n'
                                  f'❗<b>Пополните баланс для игры!</b>',
                                  reply_markup=start_kb)


async def play_ssp(msg: types.Message, state: FSMContext):
    balance_user = await get_balance_user(msg.from_user.id)
    
    try:
        bet = int(msg.text)
    except ValueError:
        await msg.answer("❗Введите число")
        return
    
    if balance_user < bet:
        await msg.answer(f'💵Пополните баланс на {bet - balance_user} руб!\n'
                         f'Сделайте меньше ставку!')
        return
    elif bet < min_rate:
        await msg.answer(f'❗Минимальная ставка {min_rate} руб')
        return
    
    async with state.proxy() as data:
        data["bet"] = bet
        data["bet_start"] = bet
        
    await msg.answer("Сделайте выбор:", reply_markup=choice_kb)
    await FsmSSP.next()
        

async def result_game_ssp(call: types.CallbackQuery, state: FSMContext):
    """
    1 - STONE
    2 - SCHERE
    3 - PAPER
    """
    enemy = random.randint(1, 3)
    user_choice = call.data.split("_")[1]
    dict_game = {"stone": 1, "scissor": 2, "paper": 3}
    
    async with state.proxy() as data:
        pass
    
    # win
    if dict_game[user_choice] == 1 and enemy == 2 or dict_game[user_choice] == 2 and enemy == 3 or dict_game[user_choice] == 3 and enemy == 1:
        balance_before_win = data["bet"] * 1.35
        
        await call.message.edit_text(f'🏆Вы выиграли!\n'
                                     f'💎Ваш выиграш: <b>{balance_before_win} руб</b>',
                                     reply_markup=win_ssp)
        async with state.proxy() as data:
            data["bet"] = balance_before_win
        await FsmSSP.next()
    # lose
    elif enemy == 1 and dict_game[user_choice] == 2 or enemy == 2 and dict_game[user_choice] == 3 or enemy == 3 and dict_game[user_choice] == 1:
        await call.message.edit_text('💢Вы проиграли\n'
                                     'Попробуйте снова',
                                     reply_markup=lose_ssp)
        await unbalance(data["bet_start"], call.from_user.id)
        await FsmSSP.ssp_game.set()
        return
    # draw
    else:
        await call.message.edit_text('🚀Ничья!\n'
                                     'Попробуйте снова',
                                     reply_markup=win_ssp)
        await FsmSSP.next()


async def path_ssp(call: types.CallbackQuery, state: FSMContext):
    if call.data == "play_again_ssp":
        await call.message.edit_text("Сделайте выбор:", reply_markup=choice_kb)
        await FsmSSP.choice_user.set()
    elif call.data == "take_win":
        async with state.proxy() as data:
            pass
        
        balance_before_game = await get_balance_user(call.from_user.id)
        winning = data["bet"] - data["bet_start"]
        
        await set_balance(balance=(balance_before_game + winning), user_id=call.from_user.id)
        await call.message.edit_text(f'💎Ваш баланс пополнен на <b>{winning} руб</b>!', reply_markup=game_menu)
        await state.finish()


async def kill_bird_info(call: types.CallbackQuery):
    await call.message.edit_text("🐦Игра <b>'Попади в птицу'</b>\n\n"
                                 "<em>Нужно угадать направление птицы\n"
                                 "При выигрыше увеличивается умножение вашей ставки, неограниченный множитель!</em>",
                                 reply_markup=menu_kbg)
    await FsmKBG.kill_bird_game.set()


async def play_kbg_menu(call: types.CallbackQuery, state: FSMContext):
    global min_rate
    balance = await get_balance_user(call.from_user.id)
    
    min_rate = 10  # minimum bet to play
    
    if balance > min_rate:
        await call.message.edit_text(f'🚀У вас на счету: {await get_balance_user(call.from_user.id)} руб\n'
                                     f'Минимальная ставка: {min_rate} руб\n'
                                     f'Угадайте направление птицы, чтобы получить больше денег\n\n'
                                     f'<b>Отправьте вашу ставку:</b>')
        await FsmKBG.next()
    else:
        await call.message.edit_text("Недостаточно баланса")
        await call.message.delete()
        
        await call.message.answer(f'💢У вас на счету: {await get_balance_user(call.from_user.id)}руб\n'
                                  f'Минимальная ставка: {min_rate} руб\n\n'
                                  f'❗<b>Пополните баланс для игры!</b>',
                                  reply_markup=start_kb)
        
        
async def play_kbg(msg: types.Message, state: FSMContext):
    balance_user = await get_balance_user(msg.from_user.id)
    
    try:
        bet = int(msg.text)
    except ValueError:
        await msg.answer("❗Введите число")
        return
    
    if balance_user < bet:
        await msg.answer(f'💵Пополните баланс на {bet - balance_user} руб!\n'
                         f'Сделайте меньше ставку!')
        return
    elif bet < min_rate:
        await msg.answer(f'❗Минимальная ставка {min_rate} руб')
        return
    
    async with state.proxy() as data:
        data["factor"] = 1.2
        data["bet"] = bet
        
    await msg.answer("Сделайте выбор:", reply_markup=choice_kbg_kb)
    await FsmKBG.next()
    
    
async def result_game_kbg(call: types.CallbackQuery, state: FSMContext):
    user_choice = call.data.split("_")[1]
    bird = random.randint(1, 3)
    dict_game = {"up": 1, "left": 2, "right": 3}
    
    async with state.proxy() as data:
        pass
    
    if dict_game[user_choice] == bird:
        balance_before_win = data["bet"] * data["factor"]
        
        await call.message.edit_text(f'🏆Вы выиграли!\n'
                                     f'Ваш выиграш: <b>{balance_before_win} руб</b>\n'
                                     f'💎Следующий множитель: <b>{data["factor"] + 0.3}X</b>\n',
                                     reply_markup=win_kbg)
        async with state.proxy() as data:
            data["factor"] += 0.3
        
        await FsmKBG.next()
    elif dict_game[user_choice] != bird:
        await call.message.edit_text('💢Вы не попали\n'
                                     'Попробуйте снова',
                                     reply_markup=lose_kbg)
        await unbalance(data["bet"], call.from_user.id)
        await FsmKBG.kill_bird_game.set()
        return


async def path_kbg(call: types.CallbackQuery, state: FSMContext):
    if call.data == "play_again_kbg":
        await call.message.edit_text("Сделайте выбор:", reply_markup=choice_kbg_kb)
        await FsmKBG.choice_user.set()
    elif call.data == "take_win":
        async with state.proxy() as data:
            pass
        
        balance_before_game = await get_balance_user(call.from_user.id)
        winning = data["bet"] * data["factor"]
        
        await set_balance(balance=(balance_before_game + winning), user_id=call.from_user.id)
        await call.message.edit_text(f'💎Ваш баланс пополнен на <b>{winning} руб!</b>', reply_markup=game_menu)
        await state.finish()

        
def register_game_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(go_to_menu, text="go_to_game_menu", state="*")
    dp.register_message_handler(go_to_menu, Text(equals=["Мини игры", "Выбрать другую игру"]), state="*")
    
    dp.register_callback_query_handler(ssp_info, text="stone_scissor_paper")
    dp.register_callback_query_handler(play_ssp_menu, text="go_to_play_ssp", state=FsmSSP.ssp_game)
    dp.register_message_handler(play_ssp, content_types=["text"], state=FsmSSP.set_bet_to_game)
    dp.register_callback_query_handler(result_game_ssp, text_contains=["choicessp_"], state=FsmSSP.choice_user)
    dp.register_callback_query_handler(path_ssp, text=["play_again_ssp", "take_win"], state=FsmSSP.select_path)
    
    dp.register_callback_query_handler(kill_bird_info, text="kill_bird")
    dp.register_callback_query_handler(play_kbg_menu, text="go_to_play_kbg", state=FsmKBG.kill_bird_game)
    dp.register_message_handler(play_kbg, content_types=["text"], state=FsmKBG.set_bet_to_game)
    dp.register_callback_query_handler(result_game_kbg, text_contains=["choicekbg_"], state=FsmKBG.choice_user)
    dp.register_callback_query_handler(path_kbg, text=["play_again_kbg", "take_win"], state=FsmKBG.select_path)
    

