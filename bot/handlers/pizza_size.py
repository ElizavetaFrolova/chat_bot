import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus

from bot.domain.order_state import OrderState


class PizzaSizeHandler(Handler):
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

        if state != OrderState.WAIT_FOR_PIZZA_SIZE:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("size_")

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        size_mapping = {
            "size_small": "Personal 🍕",
            "size_medium": "Medium 👨‍👩‍👧",
            "size_large": "Large 👨‍👩‍👧‍👦",
            "size_xl": "Party Size 🎉",
        }

        pizza_size = size_mapping.get(callback_data)
        order_json["pizza_size"] = pizza_size
        storage.update_user_order_json(telegram_id, order_json)
        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_DRINKS)

        messenger.answerCallbackQuery(update["callback_query"]["id"])

        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        messenger.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            text="Great size! 🎯 Would you like something to drink with your pizza?",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Coca-Cola 🥤",
                                "callback_data": "drink_coca_cola",
                            },
                            {"text": "Pepsi 🥤", "callback_data": "drink_pepsi"},
                        ],
                        [
                            {
                                "text": "Orange Juice 🍊",
                                "callback_data": "drink_orange_juice",
                            },
                            {
                                "text": "Apple Juice 🍎",
                                "callback_data": "drink_apple_juice",
                            },
                        ],
                        [
                            {
                                "text": "Sparkling Water 💧",
                                "callback_data": "drink_water",
                            },
                            {"text": "Iced Tea 🍵", "callback_data": "drink_iced_tea"},
                        ],
                        [
                            {
                                "text": "Just pizza, no drinks ❌",
                                "callback_data": "drink_none",
                            },
                        ],
                    ],
                },
            ),
        )
        return HandlerStatus.STOP
