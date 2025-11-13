import json
import os
import urllib.request

from dotenv import load_dotenv

from bot.domain.messenger import Messenger

load_dotenv()


class MessengerTelegram(Messenger):
    def _get_telegram_base_uri(self) -> str:
        return f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

    def _get_telegram_file_uri(self) -> str:
        return f"https://api.telegram.org/file/bot{os.getenv('TELEGRAM_TOKEN')}"

    def makeRequest(self, method: str, **kwargs) -> dict:
        json_data = json.dumps(kwargs).encode("utf-8")

        request = urllib.request.Request(
            method="POST",
            url=f"{self._get_telegram_base_uri()}/{method}",
            data=json_data,
            headers={
                "Content-Type": "application/json",
            },
        )

        with urllib.request.urlopen(request) as response:
            response_body = response.read().decode("utf-8")
            response_json = json.loads(response_body)
            assert response_json["ok"] == True  # noqa: E712
            return response_json["result"]

    def sendMessage(self, chat_id: int, text: str, **kwargs) -> dict:
        return self.makeRequest("sendMessage", chat_id=chat_id, text=text, **kwargs)

    def getUpdates(self, **kwargs) -> dict:
        return self.makeRequest("getUpdates", **kwargs)

    def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict:
        return self.makeRequest(
            "answerCallbackQuery",
            callback_query_id=callback_query_id,
            **kwargs,
        )

    def deleteMessage(self, chat_id: int, message_id: int) -> dict:
        return self.makeRequest(
            "deleteMessage",
            chat_id=chat_id,
            message_id=message_id,
        )

    def send_invoice(
        self,
        chat_id: int,
        title: str,
        description: str,
        payload: str,
        provider_token: str,
        currency: str,
        prices: list,
        **kwargs,
    ) -> dict:
        telegram_prices = []
        for price in prices:
            telegram_prices.append({"label": price["label"], "amount": price["amount"]})

        return self.makeRequest(
            "sendInvoice",
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=telegram_prices,
            **kwargs,
        )

    def answer_pre_checkout_query(
        self, pre_checkout_query_id: str, ok: bool, **kwargs
    ) -> dict:
        return self.makeRequest(
            "answerPreCheckoutQuery",
            pre_checkout_query_id=pre_checkout_query_id,
            ok=ok,
            **kwargs,
        )
