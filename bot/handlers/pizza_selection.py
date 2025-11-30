import asyncio
import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus

from bot.domain.order_state import OrderState


class PizzaSelectionHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != OrderState.WAIT_FOR_PIZZA_NAME:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("pizza_")

    async def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        pizza_mapping = {
            "pizza_margherita": "Classic Margherita",
            "pizza_pepperoni": "Spicy Pepperoni",
            "pizza_quattro_stagioni": "Four Seasons",
            "pizza_capricciosa": "Chef's Special",
            "pizza_diavola": "Hot & Spicy",
            "pizza_prosciutto": "Ham Delight",
        }

        pizza_name = pizza_mapping.get(callback_data, "Unknown Pizza")

        await asyncio.gather(
        storage.update_user_order_json(telegram_id, {"pizza_name": pizza_name}),
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_SIZE),
        messenger.answerCallbackQuery(update["callback_query"]["id"]),
        )

        await asyncio.gather(
            messenger.deleteMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            ),
            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="Perfect choice! 🎯 Now select your preferred size:",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {"text": "Personal 🍕", "callback_data": "size_small"},
                                {"text": "Medium 👨‍👩‍👧", "callback_data": "size_medium"},
                            ],
                            [
                                {"text": "Large 👨‍👩‍👧‍👦", "callback_data": "size_large"},
                                {"text": "Party Size 🎉", "callback_data": "size_xl"},
                            ],
                        ],
                    },
                ),
            ),
        )    
        return HandlerStatus.STOP
