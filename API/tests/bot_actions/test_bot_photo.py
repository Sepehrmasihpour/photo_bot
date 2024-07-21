from unittest.mock import patch, Mock
from data import telegram_ids
from bot_actions import *


def test_set_chat_photo_success(mock_telegram_api):
    chat_id = "valid_chat_id"
    file_id = "valid_file_id"

    # Mock the get_photo_path function to return a valid photo path
    with patch(
        "bot_actions.get_photo_path",
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

    # Mock the get_photo_path function to return None for invalid file_id
    with patch("bot_actions.get_photo_path", return_value=None):
        # Call the function
        response = set_chat_photo(chat_id, file_id)

    # Verify the response
    assert response["ok"] is False
    assert response["error"] == "Failed to retrieve file info or store photo path"
