from abc import ABC, abstractmethod


class Messenger(ABC):
    @abstractmethod
    def sendMessage(self, chat_id: int, text: str, **kwargs) -> dict: ...

    @abstractmethod
    def getUpdates(self, **kwargs) -> dict: ...

    @abstractmethod
    def answerCallbackQuery(self, callback_query_id: str, **kwargs) -> dict: ...

    @abstractmethod
    def deleteMessage(self, chat_id: int, message_id: int) -> dict: ...

    @abstractmethod
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
    ) -> dict: ...

    @abstractmethod
    def answer_pre_checkout_query(
        self, pre_checkout_query_id: str, ok: bool, **kwargs
    ) -> dict: ...
