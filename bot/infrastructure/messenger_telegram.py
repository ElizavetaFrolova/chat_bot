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
