from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup

from bot import main
from bot.keyboards.inline import go_to_back_by_rules, select_rules
from bot.keyboards.reply import go_to_main_menu


class FsmRules(StatesGroup):
    rules = State()


async def social_media(msg: types.Message, state: FSMContext):
    text_with_social = ""
    for name_social, link_social in main.social.items():
        text_with_social += f'{name_social} - {link_social}\n'
        
    await main.bot.send_message(chat_id=msg.chat.id,
                                text=f'🪪Соц сети:\n{text_with_social}',
                                disable_web_page_preview=True,
                                parse_mode="HTML")


async def rules_menu(msg: (types.Message or types.CallbackQuery), state: FSMContext):
    if type(msg) == types.CallbackQuery:
        msg.answer = msg.message.edit_text
    else:
        await msg.answer("Правила сервиса", reply_markup=go_to_main_menu)
        
    await msg.answer("Выберите интересующее меню", reply_markup=select_rules)
    
    await FsmRules.rules.set()
    

async def requirements(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Требования к аккаунту с закрытой торговой площадкой.\n\n"
                                 "<em>Мы пополняем только российские аккаунты. "
                                 "Валютой вашего аккаунта должны быть рубли.\n\n"
                                 "Мы НЕ можем отправить средства пользователям из следующих регионов: Крым, ЛНР, ДНР "
                                 "и тем пользователям, на аккаунте которых красная табличка (КТ)</em>",
                                 reply_markup=go_to_back_by_rules)


async def where_to_get_login(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("<em>1. Запустите свой Steam клиент\n\n"
                                 "2. В правом верхнем углу нажмите на свой никнейм\n\n"
                                 "3. В открывшемся меню выберите «Об аккаунте»\n\n"
                                 "Вы попадёте на страницу, на которой будет показан ваш"
                                 "реальный логин (не никнейм)</em>",
                                 reply_markup=go_to_back_by_rules)


async def limit_on_payment(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Лимиты на пополнение аккаунтов с закрытой торговой площадкой\n\n"
                                 "<em>Минимальная сумма пополнения 100₽\n"
                                 "Максимальная сумма 15 000₽\n\n"
                                 "Если нужно больше, то советуем сделать несколько заказов.\n\n"
                                 "Так же учитывайте общий лимит для аккаунта, он составляет $500 в сутки. "
                                 "При превышении лимита мы не несём ответственность за доставку средств.</em>",
                                 reply_markup=go_to_back_by_rules)


async def no_money_came_in(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Не пришли деньги на баланс\n\n"
                                 "<em>Если Вы указали логин верно (это не никнейм) и баланс "
                                 "Вашего аккаунта - рубли (₽), пополнение происходит моментально.\n\n"
                                 "Если Вы ошиблись и указали не свой логин и он существует в Steam,"
                                 "то деньги уйдут другому человеку и вернуть их невозможно.</em>\n"
                                 "Будьте внимательны при вводе логина!",
                                 reply_markup=go_to_back_by_rules)


async def came_in_money_less(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Пришла сумма меньше\n\n"
                                 "<em>Для пополнения нам приходится конвертировать средства в разные валюты. "
                                 "Иногда из за разницы курса валют сумма может отличаться на 1-5% от указанной.</em>",
                                 reply_markup=go_to_back_by_rules)


async def how_get_balance_steam(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("<em>- Если Вы выбрали пополнение с открытой торговой площадкой, то вам передадут скины. "
                                 "Стоимость скинов будет на 13% больше, чем вы заказали, чтобы при продаже Вы получили "
                                 "нужный баланс. Для продажи скинов вам не обязательно иметь определённую игру!\n\n"
                                 "- Если Вы выбрали пополнение с закрытой торговой площадкой, то баланс будет "
                                 "автоматически зачислен в Steam.</em>",
                                 reply_markup=go_to_back_by_rules)


async def return_policy(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("<em>Если вы проигнорировали требования к аккаунту и все же попытались отправить "
                                 "себе средства, то они не дойдут. В этом случае деньги вернуться на баланс бота "
                                 "и Вы сможете повторно сделать заказ.</em>",
                                 reply_markup=go_to_back_by_rules)


def register_social_rules_handlers(dp: Dispatcher):
    dp.register_message_handler(social_media, Text(equals="Соц сети"))
    dp.register_callback_query_handler(rules_menu, text="go_to_back", state="*")
    dp.register_message_handler(rules_menu, Text(equals="❗Правила"))
    dp.register_callback_query_handler(requirements, text="requirements", state=FsmRules)
    dp.register_callback_query_handler(where_to_get_login, text="where_to_get", state=FsmRules)
    dp.register_callback_query_handler(limit_on_payment, text="limit_on_payment", state=FsmRules)
    dp.register_callback_query_handler(no_money_came_in, text="no_money_came_in", state=FsmRules)
    dp.register_callback_query_handler(came_in_money_less, text="came_in_money_less", state=FsmRules)
    dp.register_callback_query_handler(how_get_balance_steam, text="how_get_balance_steam", state=FsmRules)
    dp.register_callback_query_handler(return_policy, text="return_policy", state=FsmRules)
