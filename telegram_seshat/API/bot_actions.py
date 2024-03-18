import os
import re
from dotenv import load_dotenv
from typing import Union
from aiohttp import FormData
from urllib.parse import quote
from aiohttp import ClientSession, FormData
from pathlib import Path


load_dotenv()


# environment variable retrievals
TEST_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")


# TODO : make the sned to group and send to channel fucntion for photo the same way as send_message
# TODO: find out what is the problem with the local file procces in the send photo fucntion


# *This function sends an asynchronous HTTP request to the Telegram API.
async def make_telegram_request(url: str, method: str = "POST", data=None):
    """
    :param url: URL of the Telegram API endpoint.
    :param method: HTTP method to be used (e.g., 'GET', 'POST').
    :param data: The data to be sent in the request body.
    :return: The JSON response from the Telegram API.
    """
    async with ClientSession() as session:
        request_func = getattr(session, method.lower(), session.post)
        async with request_func(url, data=data) as response:
            if response.status != 200:
                content = await response.text()
                error_message = f"Telegram API error: {content}"
                raise Exception(error_message)
            return await response.json()


# *These are the functions that use the telegram api to send text message to pacific chat or
# *main group, main channel


# Asynchronously sends a message to a specified chat via the Telegram Bot API.
async def send_message_via_bot(message: str, chat_id: Union[str, int]):
    encoded_message = quote(message)  # URL encode the message
    url = f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={encoded_message}"
    # Make the request to the Telegram API
    try:
        response_json = await make_telegram_request(url)
        return {"message": "Message sent successfully", "result": response_json}
    except Exception as e:
        return {"error": str(e)}


# *These are the functions that will use the telegram api to send/post
# *photos to pacific chat or main group or main channel


# !This function local file photo dose not work fix it later
async def send_photo_via_bot(photo, chat_id, caption=None):
    """
    Sends a photo message to a specified chat via Telegram bot. The photo can be a file on the local system,
    a URL, or a file_id of a photo already uploaded to Telegram servers.

    :param photo: Path to the photo, URL, or file_id.
    :param chat_id: Unique identifier for the target chat.
    :param caption: Optional. Photo caption (may also be used when resending photos by file_id).
    """
    url = f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendPhoto"
    data = FormData()

    # Determine if 'photo' is a local file, URL, or file_id
    if Path(rf"{photo}").is_file():  # Checking if it's a file
        print("Detected as Local File")
        with open(photo, "rb") as file:
            data.add_field("photo", file, filename=Path(photo).name)
    elif re.match(
        r"^[a-zA-Z0-9_-]+$", photo
    ):  # Assuming file_id has a specific pattern
        print("Detected as file_id")
        data.add_field("photo", photo)
    elif re.match(r"^https?://", photo):  # URL
        print("Detected as URL")
        data.add_field("photo", photo)
    else:
        return {"error": "Photo type could not be determined"}

    # Add chat_id and optional caption to the FormData
    data.add_field("chat_id", str(chat_id))
    if caption:
        data.add_field("caption", caption)

    # Make the request to the Telegram API
    try:
        response_json = await make_telegram_request(url, data=data)
        return {"message": "Photo sent successfully", "result": response_json}
    except Exception as e:
        return {"error": str(e)}
