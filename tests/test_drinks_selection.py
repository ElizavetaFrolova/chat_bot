from bot.dispatcher import Dispatcher
from bot.handlers.drink import DrinksSelectionHandler
from tests.mocks import Mock


def test_drinks_selection_handler():
    test_update = {
        "update_id": 123456789,
        "callback_query": {
            "id": "callback789",
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
                "message_id": 300,
            },
            "data": "drink_coca_cola",
        },
    }

    update_order_json_called = False
    update_user_state_called = False
    answer_callback_called = False
    delete_message_called = False

    def update_user_order_json(telegram_id: int, order_data: dict) -> None:
        assert telegram_id == 12345
        assert order_data == {
            "pizza_name": "Margherita",
            "pizza_size": "Large (35cm)",
            "drink": "Coca-Cola",
        }

        nonlocal update_order_json_called
        update_order_json_called = True

    def update_user_state(telegram_id: int, state: str) -> None:
        assert telegram_id == 12345
        assert state == "WAIT_FOR_ORDER_APPROVE"

        nonlocal update_user_state_called
        update_user_state_called = True

    def get_user(telegram_id: int) -> dict | None:
        assert telegram_id == 12345
        return {
            "state": "WAIT_FOR_DRINKS",
            "order_json": '{"pizza_name": "Margherita", "pizza_size": "Large (35cm)"}',
        }

    send_message_calls = []

    def sendMessage(chat_id: int, text: str, **kwargs) -> dict:
        assert chat_id == 12345
        send_message_calls.append({"text": text, "kwargs": kwargs})
        return {"ok": True}

    def answerCallbackQuery(callback_id: str) -> None:
        assert callback_id == "callback789"

        nonlocal answer_callback_called
        answer_callback_called = True

    def deleteMessage(chat_id: int, message_id: int) -> None:
        assert chat_id == 12345
        assert message_id == 300

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
            "sendMessage": sendMessage,
            "answerCallbackQuery": answerCallbackQuery,
            "deleteMessage": deleteMessage,
        }
    )

    dispatcher = Dispatcher(mock_storage, mock_messenger)
    dispatcher.add_handlers(DrinksSelectionHandler())

    dispatcher.dispatch(test_update)

    assert update_order_json_called
    assert update_user_state_called
    assert answer_callback_called
    assert delete_message_called

    assert len(send_message_calls) == 1

    message_text = send_message_calls[0]["text"]
    assert "Your Order Summary:" in message_text
    assert "**Pizza:** Margherita" in message_text
    assert "**Size:** Large (35cm)" in message_text
    assert "**Drink:** Coca-Cola" in message_text
    assert "Is everything correct?" in message_text
