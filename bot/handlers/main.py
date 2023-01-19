from aiogram import Dispatcher

from bot.handlers.admin import register_admin_handlers
from bot.handlers.user import register_user_handlers, register_balance_out_handlers, register_profile_handlers,\
    register_top_up_balance_steam_handlers, register_trade_case_handlers
from bot.handlers.other import register_other_handlers


def register_all_handlers(dp: Dispatcher) -> None:
    handlers = (
        register_admin_handlers,
        register_user_handlers,
        register_balance_out_handlers,
        register_profile_handlers,
        register_top_up_balance_steam_handlers,
        register_trade_case_handlers,
        register_other_handlers,
    )
    for handler in handlers:
        handler(dp)