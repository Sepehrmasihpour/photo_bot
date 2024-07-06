import pytest
from unittest.mock import patch
from bot_actions import (
    store_file_path,
    delete_file_path,
    set_chat_photo,
)  # Adjust the import as necessary


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
        if (
            params["chat_id"] == "valid_chat_id"
            and params["photo"] == "valid_photo_path"
        ):
            return {"ok": True}
        else:
            return {"ok": False, "error": "Invalid chat_id or photo"}


@pytest.fixture
def mock_telegram_api(mocker):
    mocker.patch(
        "bot_actions.telegram_api_request", side_effect=mock_telegram_api_request
    )


def test_store_file_path_success(mock_telegram_api, db_connection):
    file_id = "valid_file_id"
    expected_file_path = "documents/file_1.txt"

    # Call the function
    store_file_path(file_id)

    # Verify the database insert was called with correct values
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT file_id, file_path FROM photos WHERE file_id = ?", (file_id,)
    )
    result = cursor.fetchone()
    assert result["file_id"] == file_id
    assert result["file_path"] == expected_file_path


def test_store_file_path_invalid_file_id(mock_telegram_api, db_connection, capsys):
    file_id = "invalid_file_id"

    # Call the function
    store_file_path(file_id)

    # Verify no database insert was called
    cursor = db_connection.cursor()
    cursor.execute(
        "SELECT file_id, file_path FROM photos WHERE file_id = ?", (file_id,)
    )
    result = cursor.fetchone()
    assert result is None

    # Capture the output
    captured = capsys.readouterr()
    assert "Failed to get file info: Invalid file_id" in captured.out


def test_delete_file_path(mock_telegram_api, db_connection):
    file_id = "valid_file_id"
    file_path = "documents/file_1.txt"

    # Insert a file record to delete
    cursor = db_connection.cursor()
    cursor.execute(
        "INSERT INTO photos (file_id, file_path) VALUES (?, ?)", (file_id, file_path)
    )
    db_connection.commit()

    # Call the function
    delete_file_path(file_id)

    # Verify the database delete was called correctly
    cursor.execute(
        "SELECT file_id, file_path FROM photos WHERE file_id = ?", (file_id,)
    )
    result = cursor.fetchone()
    assert result is None


def test_set_chat_photo_success(mock_telegram_api):
    chat_id = "valid_chat_id"
    file_path = "valid_photo_path"

    # Call the function
    response = set_chat_photo(chat_id, file_path)

    # Verify the response
    assert response["ok"] is True


def test_set_chat_photo_invalid(mock_telegram_api):
    chat_id = "invalid_chat_id"
    file_path = "invalid_photo_path"

    # Call the function
    response = set_chat_photo(chat_id, file_path)

    # Verify the response
    assert response["ok"] is False
    assert response["error"] == "Invalid chat_id or photo"
