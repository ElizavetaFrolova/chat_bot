import pytest

from bot.dispatcher import Dispatcher
from bot.domain.order_state import OrderState
from bot.handlers.pizza_selection import PizzaSelectionHandler
from tests.mocks import Mock


@pytest.mark.asyncio
async def test_pizza_selection_handler():
    test_update = {
        "update_id": 123456789,
        "callback_query": {
            "id": "callback123",
            "from": {
                "id": 12345,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "message": {
                "chat": {
                    "id": 12345,
                    "first_name": "Test",
                    "username": "testuser",
                    "type": "private",
                },
                "message_id": 100,
            },
            "data": "pizza_margherita",
        },
    }

    update_order_json_called = False
    update_user_state_called = False
    answer_callback_called = False
    delete_message_called = False

    async def update_user_order_json(telegram_id: int, order_data: dict) -> None:
        assert telegram_id == 12345
        assert order_data == {"pizza_name": "Classic Margherita"}

        nonlocal update_order_json_called
        update_order_json_called = True

    async def update_user_state(telegram_id: int, state: OrderState) -> None:
        assert telegram_id == 12345
        assert state == OrderState.WAIT_FOR_PIZZA_SIZE

        nonlocal update_user_state_called
        update_user_state_called = True

    async def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {"state": "WAIT_FOR_PIZZA_NAME", "order_json": "{}"}

    send_message_calls = []

    async def send_message(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    async def answer_callback_query(callback_id: str) -> None:
        assert callback_id == "callback123"

        nonlocal answer_callback_called
        answer_callback_called = True

    async def delete_message(chat_id: int, message_id: int) -> None:
        assert chat_id == 12345
        assert message_id == 100

        nonlocal delete_message_called
        delete_message_called = True

    mock_storage = Mock(
        {
            "update_user_order_json": update_user_order_json,
            "update_user_state": update_user_state,
            "get_user": get_user,
        }
    )
    mock_messenger = Mock(
        {
            "send_message": send_message,
            "answer_callback_query": answer_callback_query,
            "delete_message": delete_message,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(PizzaSelectionHandler())

    await dispatcher.dispatch(test_update)

    assert update_order_json_called
    assert update_user_state_called
    assert answer_callback_called
    assert delete_message_called

    assert len(send_message_calls) == 1
    assert (
        send_message_calls[0]["text"]
        == "Perfect choice! 🎯 Now select your preferred size:"
    )
