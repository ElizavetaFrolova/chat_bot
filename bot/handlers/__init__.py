from bot.handlers.handler import Handler
from bot.handlers.message_db import UpdateDatabaseLogger
from bot.handlers.ensure_user_exists import EnsureUserExists
from bot.handlers.message_start import MessageStart
from bot.handlers.pizza_selection import PizzaSelectionHandler
from bot.handlers.pizza_size import PizzaSizeHandler
from bot.handlers.drink import DrinksSelectionHandler
from bot.handlers.finish import OrderApprovalHandler


def get_handlers() -> list[Handler]:
    return [
        UpdateDatabaseLogger(),
        EnsureUserExists(),
        MessageStart(),
        PizzaSelectionHandler(),
        PizzaSizeHandler(),
        DrinksSelectionHandler(),
        OrderApprovalHandler(),
    ]
