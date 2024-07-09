import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from main import app
from bot_actions import set_chat_photo, store_photo_path

client = TestClient(app)

#! Bad tests, make an actual real life test without mocking the functions and results. these don't work well

# Mock Data
MOCK_FILE_ID = "mock_file_id"
MOCK_GROUP_ID = "mock_group_id"
MOCK_PHOTO_PATH = "mock_photo_path"
MOCK_DOWNLOAD_URL = f"https://api.telegram.org/file/bot{{BOT_TOKEN}}/{MOCK_PHOTO_PATH}"
MOCK_API_RESPONSE = {"ok": True, "result": {"file_path": MOCK_PHOTO_PATH}}
VALID_PHOTO_CONTENT = (
    b"valid photo content that meets size requirements"  # Mock valid photo content
)
PHOTO_CROP_SIZE_SMALL_ERROR = {
    "ok": False,
    "error_code": 400,
    "description": "Bad Request: PHOTO_CROP_SIZE_SMALL",
}


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


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock:
        yield mock


def test_change_group_photo_success(
    mock_set_chat_photo, mock_store_photo_path, mock_requests_get
):
    mock_store_photo_path.return_value = MOCK_DOWNLOAD_URL
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.content = VALID_PHOTO_CONTENT
    mock_set_chat_photo.return_value = {"ok": True}

    response = client.post(f"/changGroupPhoto?file_id={MOCK_FILE_ID}")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_change_group_photo_failure(
    mock_set_chat_photo, mock_store_photo_path, mock_requests_get
):
    mock_store_photo_path.return_value = MOCK_DOWNLOAD_URL
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.content = VALID_PHOTO_CONTENT
    mock_set_chat_photo.return_value = {
        "ok": False,
        "error": "Failed to set chat photo",
    }

    response = client.post(f"/changGroupPhoto?file_id={MOCK_FILE_ID}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Failed to set chat photo"


def test_change_group_photo_photo_crop_size_small_error(
    mock_set_chat_photo, mock_store_photo_path, mock_requests_get
):
    mock_store_photo_path.return_value = MOCK_DOWNLOAD_URL
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.content = VALID_PHOTO_CONTENT
    mock_set_chat_photo.return_value = PHOTO_CROP_SIZE_SMALL_ERROR

    response = client.post(f"/changGroupPhoto?file_id={MOCK_FILE_ID}")
    assert response.status_code == 400
    assert (
        response.json()["detail"]
        == "The photo size is not within the acceptable limits (160x160 to 2048x2048 pixels)."
    )


def test_change_group_photo_exception(
    mock_set_chat_photo, mock_store_photo_path, mock_requests_get
):
    mock_store_photo_path.return_value = MOCK_DOWNLOAD_URL
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.content = VALID_PHOTO_CONTENT
    mock_set_chat_photo.side_effect = Exception("Unexpected error")

    response = client.post(f"/changGroupPhoto?file_id={MOCK_FILE_ID}")
    assert response.status_code == 500
    assert response.json()["detail"] == "Unexpected error"
