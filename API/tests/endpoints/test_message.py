# tests/test_message_group.py
import pytest
from unittest.mock import patch

# Sample data for testing
GROUP_ID = "12345678"
MEDIA_URL = "http://example.com/media.jpg"
CAPTION = "This is a caption"
MEDIA_TYPES = ["photo", "text", "audio", "video"]


# Mock function to simulate send_media_via_bot behavior
def mock_send_media_via_bot(media, media_type, chat_id, caption=None, test=False):
    if media_type not in MEDIA_TYPES:
        return {"error": "unacceptable media type"}
    if media == "invalid":
        return {"error": "Invalid media"}
    return {"ok": True, "result": "success"}


@pytest.mark.parametrize("media_type", MEDIA_TYPES)
def test_message_group_success(client, media_type):
    with patch("main.send_media_via_bot", side_effect=mock_send_media_via_bot):
        response = client.post(
            f"/message/{media_type}", data={"media": MEDIA_URL, "caption": CAPTION}
        )
        assert response.status_code == 200
        assert response.json() == {"ok": True, "result": "success"}


def test_message_group_invalid_media_type(client):
    invalid_media_type = "invalid_media"
    with patch("main.send_media_via_bot", side_effect=mock_send_media_via_bot):
        response = client.post(
            f"/message/{invalid_media_type}",
            data={"media": MEDIA_URL, "caption": CAPTION},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "unacceptable media type"}


def test_message_group_invalid_media(client):
    media_type = "photo"
    invalid_media = "invalid"
    with patch("main.send_media_via_bot", side_effect=mock_send_media_via_bot):
        response = client.post(
            f"/message/{media_type}",
            data={"media": invalid_media, "caption": CAPTION},
        )
        assert response.status_code == 400
        assert response.json() == {"detail": "Invalid media"}


def test_message_group_no_caption(client):
    media_type = "photo"
    with patch("main.send_media_via_bot", side_effect=mock_send_media_via_bot):
        response = client.post(f"/message/{media_type}", data={"media": MEDIA_URL})
        assert response.status_code == 200
        assert response.json() == {"ok": True, "result": "success"}
