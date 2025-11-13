import json

from bot.domain.messenger import Messenger
from bot.domain.order_state import OrderState
from bot.domain.storage import Storage
from bot.handlers.handler import Handler, HandlerStatus


class SuccessfulPaymentHandler(Handler):
    def can_handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> bool:
        if "message" not in update:
            return False

        return "successful_payment" in update["message"]

    def handle(
        self,
        update: dict,
        state: OrderState,
        order_json: dict,
        storage: Storage,
        messenger: Messenger,
    ) -> HandlerStatus:
        telegram_id = update["message"]["from"]["id"]
        successful_payment = update["message"]["successful_payment"]

        invoice_payload = successful_payment["invoice_payload"]
        try:
            payload = json.loads(invoice_payload)
            pizza_name = payload.get("pizza_name", "Unknown")
            pizza_size = payload.get("pizza_size", "Unknown")
            drink = payload.get("drink", "Unknown")
        except json.JSONDecodeError:
            user_data = storage.get_user(telegram_id)
            if user_data and user_data.get("order_json"):
                order_data = json.loads(user_data["order_json"])
                pizza_name = order_data.get("pizza_name", "Unknown")
                pizza_size = order_data.get("pizza_size", "Unknown")
                drink = order_data.get("drink", "Unknown")
            else:
                pizza_name = "Unknown"
                pizza_size = "Unknown"
                drink = "Unknown"

        storage.update_user_state(telegram_id, OrderState.ORDER_FINISHED)

        order_confirmation = f"""✅ **Order Confirmed!**
🍕 **Your Order:**
• Pizza: {pizza_name}
• Size: {pizza_size}
• Drink: {drink}

Thank you for your payment! Your pizza will be ready soon.

Send /start to place another order."""

        messenger.sendMessage(
            chat_id=update["message"]["chat"]["id"],
            text=order_confirmation,
            parse_mode="Markdown",
        )

        return HandlerStatus.STOP