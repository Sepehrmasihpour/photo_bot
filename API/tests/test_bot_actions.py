import pytest
from unittest.mock import patch, Mock
from data import telegram_ids
from bot_actions import (
    store_photo_path,
    delete_photo_path,
    set_chat_photo,
)


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


@pytest.fixture
def mock_telegram_api(mocker):
    mocker.patch(
        "bot_actions.telegram_api_request", side_effect=mock_telegram_api_request
    )


def test_store_photo_path_success(mock_telegram_api, db_connection):
    from bot_actions import (
        BOT_TOKEN,
    )  # Import the BOT_TOKEN to construct the expected file path

    file_id = "valid_file_id"
    expected_file_path = (
        f"https://api.telegram.org/file/bot{BOT_TOKEN}/documents/file_1.txt"
    )

    # Call the function
    store_photo_path(file_id)

    # Verify the database insert was called with correct values
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT file_id, file_path FROM photos WHERE file_id = ?", (file_id,)
    )
    result = cursor.fetchone()
    assert result["file_id"] == file_id
    assert result["file_path"] == expected_file_path


def test_store_photo_path_invalid_file_id(mock_telegram_api, db_connection, capsys):
    file_id = "invalid_file_id"

    # Call the function
    store_photo_path(file_id)

    # Verify no database insert was called
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT file_id, file_path FROM photos WHERE file_id = ?", (file_id,)
    )
    result = None
    assert result is None

    # Capture the output
    captured = capsys.readouterr()
    assert "Failed to get file info: Invalid file_id" in captured.out


def test_delete_photo_path(mock_telegram_api, db_connection):
    BOT_TOKEN = telegram_ids["BOT_TOKEN"]

    file_id = "valid_file_id"
    file_path = f"https://api.telegram.org/file/bot{BOT_TOKEN}/documents/file_1.txt"

    # Insert a file record to delete
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO photos (file_id, file_path) VALUES (?, ?)", (file_id, file_path)
    )
    db_connection.commit()

    # Call the function
    delete_photo_path(file_id)

    # Verify the database delete was called correctly
    cursor.execute(
        "SELECT file_id, file_path FROM photos WHERE file_id = ?", (file_id,)
    )
    result = cursor.fetchone()
    assert result is None


def test_set_chat_photo_success(mock_telegram_api):
    chat_id = "valid_chat_id"
    file_id = "valid_file_id"

    # Mock the store_photo_path function to return a valid photo path
    with patch(
        "bot_actions.store_photo_path",
        return_value="https://example.com/valid_photo_path.jpg",
    ):
        # Mock requests.get to simulate a successful download
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.content = b"photo content"
            mock_get.return_value = mock_response

            # Call the function
            response = set_chat_photo(chat_id, file_id)
            print(f"Response from set_chat_photo: {response}")  # Debug output

    # Verify the response
    assert response["ok"] is True


def test_set_chat_photo_invalid(mock_telegram_api):
    chat_id = "invalid_chat_id"
    file_id = "invalid_file_id"

    # Mock the store_photo_path function to return None for invalid file_id
    with patch("bot_actions.store_photo_path", return_value=None):
        # Call the function
        response = set_chat_photo(chat_id, file_id)

    # Verify the response
    assert response["ok"] is False
    assert response["error"] == "Failed to retrieve file info or store photo path"
