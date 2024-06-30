import pytest
from unittest.mock import patch
from bot_actions import store_file_path  # Adjust the import as necessary


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
