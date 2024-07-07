import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from bot_actions import set_chat_photo, store_photo_path

client = TestClient(app)

# Mock Data
MOCK_FILE_ID = "mock_file_id"
MOCK_GROUP_ID = "mock_group_id"
MOCK_PHOTO_PATH = "mock_photo_path"
MOCK_DOWNLOAD_URL = f"https://api.telegram.org/file/bot{{BOT_TOKEN}}/{MOCK_PHOTO_PATH}"
MOCK_API_RESPONSE = {"ok": True, "result": {"file_path": MOCK_PHOTO_PATH}}


# Mock telegram_api_request function
@pytest.fixture
def mock_telegram_api_request():
    with patch("bot_actions.telegram_api_request") as mock:
        yield mock


@pytest.fixture
def mock_store_photo_path():
    with patch("bot_actions.store_photo_path") as mock:
        yield mock


@pytest.fixture
def mock_set_chat_photo():
    with patch("bot_actions.set_chat_photo") as mock:
        yield mock


def test_change_group_photo_success(mock_set_chat_photo, mock_store_photo_path):
    mock_store_photo_path.return_value = MOCK_DOWNLOAD_URL
    mock_set_chat_photo.return_value = {"ok": True}

    response = client.post(f"/changGroupPhoto?file_id={MOCK_FILE_ID}")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_change_group_photo_failure(mock_set_chat_photo, mock_store_photo_path):
    mock_store_photo_path.return_value = MOCK_DOWNLOAD_URL
    mock_set_chat_photo.return_value = {
        "ok": False,
        "error": "Failed to set chat photo",
    }

    response = client.post(f"/changGroupPhoto?file_id={MOCK_FILE_ID}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to set chat photo"


def test_change_group_photo_exception(mock_set_chat_photo, mock_store_photo_path):
    mock_store_photo_path.return_value = MOCK_DOWNLOAD_URL
    mock_set_chat_photo.side_effect = Exception("Unexpected error")

    response = client.post(f"/changGroupPhoto?file_id={MOCK_FILE_ID}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error"
