import logging
import os
import time

import aiohttp
from dotenv import load_dotenv

from bot.domain.messenger import Messenger

load_dotenv()

# Настройка логирования для HTTP запросов
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s.%(msecs)03d] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class MessengerTelegram(Messenger):
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    def _get_telegram_base_uri(self) -> str:
        return f"https://api.telegram.org/bot{os.getenv('TELEGRAM_TOKEN')}"

    def _get_telegram_file_uri(self) -> str:
        return f"https://api.telegram.org/file/bot{os.getenv('TELEGRAM_TOKEN')}"

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def makeRequest(self, method: str, **kwargs) -> dict:
        url = f"{self._get_telegram_base_uri()}/{method}"
        start_time = time.time()

        logger.info(f"[HTTP] → POST {method}")

        try:
            session = await self._get_session()
            async with session.post(
                url,
                json=kwargs,
                headers={"Content-Type": "application/json"},
            ) as response:
                response_json = await response.json()
                assert response_json["ok"] == True  # noqa: E712

                duration_ms = (time.time() - start_time) * 1000
                logger.info(f"[HTTP] ← POST {method} - {duration_ms:.2f}ms")

                return response_json["result"]
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            logger.error(f"[HTTP] ✗ POST {method} - {duration_ms:.2f}ms - Error: {e}")
            raise

    async def close(self) -> None:
        """Закрыть HTTP сессию."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def sendMessage(self, chat_id: int, text: str, **kwargs) -> dict:
        """
        https://core.telegram.org/bots/api#sendmessage
        """
        return await self.makeRequest(
            "sendMessage", chat_id=chat_id, text=text, **kwargs
        )

    async def getUpdates(self, **kwargs) -> list:
        """
        https://core.telegram.org/bots/api#getupdates
        """
        return await self.makeRequest("getUpdates", **kwargs)

    async def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict:
        """
        https://core.telegram.org/bots/api#answercallbackquery
        """
        return await self.makeRequest(
            "answerCallbackQuery",
            callback_query_id=callback_query_id,
            **kwargs,
        )

    async def deleteMessage(self, chat_id: int, message_id: int) -> dict:
        """
        https://core.telegram.org/bots/api#deletemessage
        """
        return await self.makeRequest(
            "deleteMessage",
            chat_id=chat_id,
            message_id=message_id,
        )

    async def send_invoice(
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
        """
        https://core.telegram.org/bots/api#sendinvoice
        """
        return await self.makeRequest(
            "sendInvoice",
            chat_id=chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=provider_token,
            currency=currency,
            prices=prices,
            **kwargs,
        )

    async def answer_pre_checkout_query(
        self, pre_checkout_query_id: str, ok: bool, **kwargs
    ) -> dict:
        """
        https://core.telegram.org/bots/api#answerprecheckoutquery
        """
        return await self.makeRequest(
            "answerPreCheckoutQuery",
            pre_checkout_query_id=pre_checkout_query_id,
            ok=ok,
            **kwargs,
        )
