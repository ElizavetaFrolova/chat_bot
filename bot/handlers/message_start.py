import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class MessageStart(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        return (
            "message" in update
            and "text" in update["message"]
            and update["message"]["text"] == "/start"
        )

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]

        storage.clear_user_order_json(telegram_id)
        storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

        messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="🍕 Welcome to Pizza Palace! 🍕",
            reply_markup=json.dumps({"remove_keyboard": True}),
        )

        messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text="What delicious pizza would you like to order today?",
            reply_markup=json.dumps(
                {
                    "inline_keyboard": [
                        [
                            {
                                "text": "Classic Margherita",
                                "callback_data": "pizza_margherita",
                            },
                            {
                                "text": "Spicy Pepperoni",
                                "callback_data": "pizza_pepperoni",
                            },
                        ],
                        [
                            {
                                "text": "Four Seasons",
                                "callback_data": "pizza_quattro_stagioni",
                            },
                            {
                                "text": "Chef's Special",
                                "callback_data": "pizza_capricciosa",
                            },
                        ],
                        [
                            {"text": "Hot & Spicy", "callback_data": "pizza_diavola"},
                            {
                                "text": "Ham Delight",
                                "callback_data": "pizza_prosciutto",
                            },
                        ],
                    ],
                },
            ),
        )
        return HandlerStatus.STOP
