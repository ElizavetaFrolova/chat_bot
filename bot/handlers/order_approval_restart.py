import json

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderApprovalRestartHandler(Handler):
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

        if state != OrderState.WAIT_FOR_ORDER_APPROVE:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data == "order_restart"

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]

        messenger.answerCallbackQuery(update["callback_query"]["id"])
        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        storage.clear_user_order_json(telegram_id)

        storage.update_user_state(telegram_id, OrderState.WAIT_FOR_PIZZA_NAME)

        messenger.sendMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
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
                            {
                                "text": "Hot & Spicy", 
                                "callback_data": "pizza_diavola"
                            },
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