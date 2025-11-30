import asyncio
import json

from bot.domain.messenger import Messenger
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus

from bot.domain.order_state import OrderState


class DrinksSelectionHandler(Handler):
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

        if state != OrderState.WAIT_FOR_DRINKS:
            return False

        callback_data = update["callback_query"]["data"]
        return callback_data.startswith("drink_")

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

        drink_mapping = {
            "drink_coca_cola": "Coca-Cola 🥤",
            "drink_pepsi": "Pepsi 🥤",
            "drink_orange_juice": "Orange Juice 🍊",
            "drink_apple_juice": "Apple Juice 🍎",
            "drink_water": "Sparkling Water 💧",
            "drink_iced_tea": "Iced Tea 🍵",
            "drink_none": "Just pizza, no drinks ❌",
        }
        selected_drink = drink_mapping.get(callback_data)

        order_json["drink"] = selected_drink

        await asyncio.gather(
            storage.update_user_order_json(telegram_id, order_json),
            storage.update_user_state(telegram_id, OrderState.WAIT_FOR_ORDER_APPROVE),
            messenger.answerCallbackQuery(update["callback_query"]["id"]),
        )

        pizza_name = order_json.get("pizza_name", "Unknown")
        pizza_size = order_json.get("pizza_size", "Unknown")
        drink = order_json.get("drink", "Unknown")

        order_summary = f"""🎉 **Your Order is Ready!**

    🍕 **Pizza:** {pizza_name}
    📏 **Size:** {pizza_size}
    🥤 **Drink:** {drink}

    Does everything look perfect?"""
        
        await asyncio.gather(

            messenger.deleteMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                message_id=update["callback_query"]["message"]["message_id"],
            ),

            messenger.sendMessage(
                chat_id=update["callback_query"]["message"]["chat"]["id"],
                text=order_summary,
                parse_mode="Markdown",
                reply_markup=json.dumps(
                    {
                        "inline_keyboard": [
                            [
                                {
                                    "text": "✅ Yes, perfect!",
                                    "callback_data": "order_approve",
                                },
                                {
                                    "text": "🔄 Start over",
                                    "callback_data": "order_restart",
                                },
                            ],
                        ],
                    },
                ),
            ),
        )
        return HandlerStatus.STOP
