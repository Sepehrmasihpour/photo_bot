from unittest.mock import patch, Mock
from data import telegram_ids
from bot_actions import *


def test_post_poll_success(mock_telegram_api):
    question = "What's your favorite programming language?"
    options = ["Python", "JavaScript", "C++", "Java"]
    is_anonymous = True

    response = post_poll(question, options, is_anonymous)

    assert response["ok"] is True
    assert "poll_id" in response["result"]


def test_post_poll_invalid_data(mock_telegram_api):
    question = ""
    options = []
    is_anonymous = True

    response = post_poll(question, options, is_anonymous)

    assert response["ok"] is False
    assert response["error"] == "Invalid poll data"


def test_post_poll_network_error(mock_telegram_api):
    with patch(
        "bot_actions.telegram_api_request", side_effect=Exception("Network error")
    ):
        question = "What's your favorite programming language?"
        options = ["Python", "JavaScript", "C++", "Java"]
        is_anonymous = True

        response = post_poll(question, options, is_anonymous)

        assert response["ok"] is False
        assert response["error"] == "Network error"


def test_get_poll_results_success(mock_telegram_api):
    message_id = "valid_message_id"

    response = get_poll_results(message_id)

    assert response["ok"] is True
    assert "result" in response
    assert response["result"]["id"] == "poll_id"
    assert len(response["result"]["options"]) == 2


def test_get_poll_results_network_error(mock_telegram_api):
    with patch(
        "bot_actions.telegram_api_request", side_effect=Exception("Network error")
    ):
        message_id = "valid_message_id"

        response = get_poll_results(message_id)

        assert response["ok"] is False
        assert response["error"] == "Network error"


def test_stop_poll_success(mock_telegram_api):
    message_id = "valid_message_id"

    response = stop_poll(message_id)

    assert response["ok"] is True
    assert response["result"]["poll_id"] == message_id
    assert response["result"]["is_closed"] is True


def test_stop_poll_network_error(mock_telegram_api):
    with patch(
        "bot_actions.telegram_api_request", side_effect=Exception("Network error")
    ):
        message_id = "valid_message_id"

        response = stop_poll(message_id)

        assert response["ok"] is False
        assert response["error"] == "Network error"
