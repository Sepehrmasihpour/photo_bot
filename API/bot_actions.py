from typing import IO
from data import telegram_ids
import httpx
from typing import Optional, Dict, Any


# Extracting the BOT_TOKEN from the data module.
BOT_TOKEN = telegram_ids["BOT_TOKEN"]
TEST_USER_BOT_TOKEN = telegram_ids["TEST_USER_BOT_TOKEN"]


# ! make a function for sneding telegram requests geres otherwise it will be repeated over and over again
#! make it so that it will have a request argument with the type string and basicly use the logic in the send_media_via_bot function to make it


def telegram_api_request(
    request: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    test_user: bool = False,
):
    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/{request}"
        if not test_user
        else f"https://api.telegram.org/bot{TEST_USER_BOT_TOKEN}/{request}"
    )
    try:
        if method.upper() == "POST":
            response = httpx.post(url, params=params, data=data, files=files)
        else:
            response = httpx.get(url, params=params)
        response_json = response.json()
        return response_json
    except Exception as e:
        return {"error": str(e)}


def send_media_via_bot(
    media: str | IO[any],
    media_type: str,
    chat_id: str | int,
    caption: str | None = None,
    test: bool = False,  #!This is only for testing and should it will change the default sender of the message from the to another bot. (test_purposes only)
):
    # List of supported media types
    media_types = ["photo", "text", "audio", "video"]

    # Converting the input media type to lowercase
    input_media_type = media_type.lower()

    # Checking if the input media type is valid
    if input_media_type in media_types:
        # Constructing the request URL based on the media type.
        request = (
            f"send{input_media_type.capitalize()}"
            if input_media_type != "text"
            else f"sendMessage"
        )
        data = {"chat_id": chat_id}
        files = None

        if input_media_type != "text":
            if isinstance(media, str):  # Assuming media as URL or file_id
                data[input_media_type] = media
            else:  # Assuming media is an opened file
                files = {input_media_type: media}
        else:
            data["text"] = (
                media  # In case of text, the message content goes directly into data
            )

        if caption:
            data["caption"] = caption

        return (
            telegram_api_request(request, "POST", data=data, files=files)
            if not test
            else telegram_api_request(
                request, "POST", data=data, files=files, test_user=True
            )
        )

    else:
        # Returning error response for unsupported media type
        return {"error": "unacceptable media type"}


def telegram_getUpdates(allowed_updates: list = [], offset: int = 0):
    request = "getUpdates"
    params = {"allowed_updates": allowed_updates, "offset": offset}
    response = telegram_api_request(request=request, params=params)
    return response
