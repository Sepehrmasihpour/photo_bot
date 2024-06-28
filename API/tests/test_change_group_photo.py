import pytest
from unittest.mock import patch


def test_change_group_photo_success(client):
    """
    Test case for successfully changing the group photo.

    Steps:
    1. Mock the set_chat_photo function to return a success response.
    2. Send a POST request to the /changGroupPhoto endpoint with a valid photo string.
    3. Assert that the response status code is 200.
    4. Assert that the response JSON matches the expected success response.
    """
    with patch(
        "main.set_chat_photo", return_value={"result": "photo set successfully"}
    ):
        response = client.post("/changGroupPhoto", params={"photo": "valid_photo_id"})
        assert response.status_code == 200
        assert response.json() == {"result": "photo set successfully"}


def test_change_group_photo_error(client):
    """
    Test case for handling error when changing the group photo.

    Steps:
    1. Mock the set_chat_photo function to return an error response.
    2. Send a POST request to the /changGroupPhoto endpoint with an invalid photo string.
    3. Assert that the response status code is 400.
    4. Assert that the response JSON contains the expected error detail.
    """
    with patch("main.set_chat_photo", return_value={"error": "invalid photo id"}):
        response = client.post("/changGroupPhoto", params={"photo": "invalid_photo_id"})
        assert response.status_code == 400
        assert response.json() == {"detail": "invalid photo id"}


def test_change_group_photo_exception(client):
    """
    Test case for handling exceptions during the photo change process.

    Steps:
    1. Mock the set_chat_photo function to raise an exception.
    2. Send a POST request to the /changGroupPhoto endpoint.
    3. Assert that the response status code is 500.
    4. Assert that the response JSON contains the expected error message.
    """
    with patch("main.set_chat_photo", side_effect=Exception("Unexpected error")):
        response = client.post("/changGroupPhoto", params={"photo": "photo_id"})
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal Server Error"}
