# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app
from bot_actions import *
from data import (
    telegram_ids,
)


@pytest.fixture(scope="session")
def client():
    """
    Fixture to create a TestClient instance for the FastAPI app.

    This client is used to send HTTP requests to the API during tests.
    The scope is 'session' to ensure a single instance is used for all tests in the session.
    """
    return TestClient(app)


@pytest.fixture(scope="module")
def telegram_ids_fixture():
    """
    Fixture to provide Telegram IDs data.

    This fixture supplies the Telegram IDs to the tests.
    The scope is 'module' to share the same data across all tests in a module.
    """
    return telegram_ids


# Mock function for telegram_api_request
def mock_telegram_api_request(
    request, method="GET", params=None, data=None, files=None, test_user=False
):
    if request == "getFile":
        if params["file_id"] == "valid_file_id":
            return {
                "ok": True,
                "result": {
                    "file_id": "valid_file_id",
                    "file_path": "documents/file_1.txt",
                },
            }
        else:
            return {"ok": False, "error": "Invalid file_id"}
    elif request == "setChatPhoto":
        return {"ok": True}
    elif request == "sendPoll":
        if params["question"] and params["options"]:
            return {"ok": True, "result": {"poll_id": "12345"}}
        else:
            return {"ok": False, "error": "Invalid poll data"}
    elif request == "getPollResults":
        return {
            "ok": True,
            "result": {
                "id": "poll_id",
                "question": "Sample Question",
                "options": [
                    {"text": "Option 1", "voter_count": 10},
                    {"text": "Option 2", "voter_count": 20},
                ],
            },
        }
    elif request == "stopPoll":
        return {
            "ok": True,
            "result": {"poll_id": params["message_id"], "is_closed": True},
        }
    return {"ok": False, "error": "Unhandled request"}


@pytest.fixture
def mock_telegram_api(mocker):
    mocker.patch(
        "bot_actions.telegram_api_request", side_effect=mock_telegram_api_request
    )
