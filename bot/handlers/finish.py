import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class OrderApprovalHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "callback_query" not in update:
            return False

        if state != "WAIT_FOR_ORDER_APPROVE":
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data in ["order_approve", "order_restart"]

    def handle(
        self,
        update: dict,
        state: str,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["callback_query"]["from"]["id"]
        callback_data = update["callback_query"]["data"]

        messenger.answerCallbackQuery(update["callback_query"]["id"])
        messenger.deleteMessage(
            chat_id=update["callback_query"]["message"]["chat"]["id"],
            message_id=update["callback_query"]["message"]["message_id"],
        )

        if callback_data == "order_approve":
            storage.update_user_state(telegram_id, "ORDER_FINISHED")

            pizza_name = order_json.get("pizza_name", "Unknown")
            pizza_size = order_json.get("pizza_size", "Unknown")
            drink = order_json.get("drink", "Unknown")

            order_confirmation = f"""🎉 **Order Confirmed! Thank You!** 🎉

🍕 **Your Delicious Order:**
• {pizza_name}
• {pizza_size}
• {drink}

⏰ Your pizza will be ready in 20-25 minutes!

Send /start to order another masterpiece! 🍕"""

            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=order_confirmation,
                parse_mode="Markdown",
            )

        elif callback_data == "order_restart":
            storage.clear_user_order_json(telegram_id)

            storage.update_user_state(telegram_id, "WAIT_FOR_PIZZA_NAME")

            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text="🍕 Welcome back! What delicious pizza would you like to order today?",
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
                                    "callback_data": "pizza_diavola",
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
