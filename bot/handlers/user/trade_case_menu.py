from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot.handlers.user.different import get_case, get_skin, get_all_price_case, send_message_all_admin
from bot.keyboards.inline import count_case, get_case_inline_kb, select_path_trade_case_kb, select_skin_kb,\
    agree_or_no, before_adding_skin, check_on_trade, no_money_for_add_skin
from bot.keyboards.reply import go_to_main_menu, select_type_market_kb


class FsmTradeCase(StatesGroup):
    case = State()
    how_much_case = State()
    select_skin_for_trade = State()
    set_trade_link = State()
    

async def trade_case(msg: types.Message):
    if type(msg) != types.CallbackQuery:
        await msg.answer("Обменять кейсы", reply_markup=go_to_main_menu)
    else:
        msg.answer = msg.message.edit_text

    await msg.answer("Выберите кейсы из вашего инвентар",
                     reply_markup=get_case_inline_kb(get_case()))
    
    await FsmTradeCase.case.set()


async def set_how_case(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if len(data) == 0:
            async with state.proxy() as data:
                data["all_case_for_trade"] = [[], []]
    
    if call.data == "case_all":
        await call.message.edit_text("Выберите кейсы из вашего инвентар",
                                     reply_markup=get_case_inline_kb(get_case(), 0))
        return
    
    case = call.data.split("_")[1]
    async with state.proxy() as data:
        try:
            data["all_case"] += [{case: 0}]
        except KeyError:
            data["all_skin"] = []
            data["all_case"] = []
            data["all_case"] += [{case: 0}]
                    
        data["case"] = case
    await call.message.edit_text(f"Выберите количество кейсов «{case}»", reply_markup=count_case())
    
    await FsmTradeCase.next()
        

async def info_about_adding(call: types.CallbackQuery, state: FSMContext):
    how_much = int(call.data.split("_")[1])
    async with state.proxy() as data:
        data["all_case"][len(data["all_case"]) - 1][data["case"]] += how_much
        data["price_select_case"] = await get_all_price_case(data['all_case'], get_case())
        
    text_with_all_case = ""
    for all_case in data["all_case"]:
        for case, count in all_case.items():
            text_with_all_case += f'Кейс:  {case} - {count}шт.\n'
        
    await call.message.edit_text(f"Вы добавили:\n"
                                 f"{text_with_all_case}",
                                 reply_markup=select_path_trade_case_kb)
    await FsmTradeCase.next()


async def add_case(call: types.CallbackQuery, state: FSMContext):
    await FsmTradeCase.first()
    await trade_case(call)


async def select_skin(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        pass
    
    try:
        await call.message.edit_text("Выберите скины которые вы хотите",
                                     reply_markup=select_skin_kb(data["price_select_case"], get_skin()))
    except ZeroDivisionError:  # if no have skin about this price
        await call.message.edit_text(f'Вы выбрали кейсов на {data["price_select_case"]}руб'
                                     f'\nВыберите больше кейсов, чтобы совершить обмен',
                                     reply_markup=get_case_inline_kb(get_case()))
        await FsmTradeCase.first()


async def agreement(call: types.CallbackQuery, state: FSMContext):
    if call.data == 'skin_all':
        async with state.proxy() as data:
            price_case = data["price_select_case"]
            await call.message.edit_text("Выберите скины которые вы хотите",
                                         reply_markup=select_skin_kb(price_case, get_skin(), 0))
        return
        
    async with state.proxy() as data:
        skin = [call.data.split("_")[1]][0]
        data["skin"] = skin
    await call.message.edit_text(f'Вы выбрали {skin}', reply_markup=agree_or_no)


async def agree_or_no_areement(call: types.CallbackQuery, state: FSMContext):
    skins_dict = get_skin()
    if call.data == "agree":
        async with state.proxy() as data:
            skin_price = skins_dict[data["skin"]]
            
            data["all_skin"] += [data["skin"]]
            data["all_case_for_trade"][0] = data["all_skin"]
            data["all_case_for_trade"][1] = data["all_case"]
            data["price_select_case"] = (data["price_select_case"] - skin_price)
            
            all_skin = str(data["all_skin"]).split("[")[1].split("]")[0]
            
            if int(data["price_select_case"]) < int(sorted((skins_dict).values())[0]) + 1:
                await call.message.edit_text(f'<em>Вы выбрали</em> <b>{all_skin}</b>'
                                             f'\nУ вас нехватает для выбора скинов!',
                                             reply_markup=no_money_for_add_skin)
                data["all_case"] = []
                return
                
            await call.message.edit_text(f'<em>Вы выбрали</em> <b>{all_skin}</b>'
                                         f'\nУ вас осталось: <b>{data["price_select_case"]}руб</b>',
                                         reply_markup=before_adding_skin)
    if call.data == "not_agree":
        async with state.proxy() as data:
            price_case = data["price_select_case"]
        try:
            await call.message.edit_text("Выберите скины которые вы хотите",
                                         reply_markup=select_skin_kb(price_case, skins_dict))
        except ZeroDivisionError:  # if no have skin about this price
            await call.message.edit_text(f'Вы выбрали кейсов на {price_case}руб'
                                         f'\nВыберите больше кейсов, чтобы совершить обмен',
                                         reply_markup=get_case_inline_kb(get_case()))
            await FsmTradeCase.first()
            return
        await FsmTradeCase.select_skin_for_trade.set()


async def go_to_trade(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Отправьте следующим сообщением вашу трейд ссылку\n"
                              "Функция нужна для прихода трейд ссылки вместе с составленным"
                              "ранее обменом, чтобы я  мог отправить его",
                              reply_markup=select_type_market_kb)
    await FsmTradeCase.next()


async def set_link(msg: types.Message, state: FSMContext):  # beed trade link
    if msg.text == "Где взять трейд-ссылку?":
        await msg.answer("https://www.youtube.com/watch?v=w3-eDOaOjx8")
        await msg.answer('Для продолжения операции отправьте вашу трейд-ссылку следующим сообщением',
                         reply_markup=go_to_main_menu)
        return
    elif msg.text.find("https://steamcommunity.com/tradeoffer/new/") == 0:
        async with state.proxy() as data:
            data["user_link"] = msg.text
        
        trade_link = 'https://www.google.com.ua/'
        async with state.proxy() as data:
            await msg.answer(f"Отправьте трейд по этой <a href=\"{trade_link}\">ССЫЛКЕ</a>",
                             reply_markup=check_on_trade)
    else:
        await msg.answer("Неправильная трейд-ссылка!\nОтправьте ссылку в правильном формате",
                         reply_markup=select_type_market_kb)
        return


async def check_trade(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Ваш запрос получен. Ожидайте обмен в течение 12 часов.")
    
    username = call.from_user.username if call.from_user.username != "None" else call.from_user.first_name
    
    async with state.proxy() as data:
        text_for_admin = (f"_❗Заявка на обмен_\n"
                          f"Telegram для связи: `@{username}`\n"
                          f"Обмен:\n"
                          f"   Скины: *{data['all_case_for_trade'][0]}*\n   Кейсы: *{data['all_case_for_trade'][1]}*"
                          f"\nCсылка на обмен: `{data['user_link']}`")
    await send_message_all_admin(text_for_admin)
    
    await state.finish()
    

def register_trade_case_handlers(dp: Dispatcher):
    dp.register_message_handler(trade_case, Text(equals='Обменять кейсы'))
    dp.register_callback_query_handler(set_how_case, text_contains='case_', state=FsmTradeCase.case)
    dp.register_callback_query_handler(info_about_adding, text_contains="count_", state=FsmTradeCase.how_much_case)
    dp.register_callback_query_handler(add_case, text='add_case', state="*")
    dp.register_callback_query_handler(select_skin, text='go_to_add_skins', state=FsmTradeCase.select_skin_for_trade)
    dp.register_callback_query_handler(agreement, text_contains=['skin_'], state=FsmTradeCase)
    dp.register_callback_query_handler(agree_or_no_areement, text=['agree', 'not_agree'], state=FsmTradeCase)
    dp.register_callback_query_handler(go_to_trade, text='go_to_trade', state=FsmTradeCase)
    dp.register_message_handler(set_link, state=FsmTradeCase.set_trade_link)
    dp.register_callback_query_handler(check_trade, text='check_trade', state=FsmTradeCase)
    