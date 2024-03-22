import os
from dotenv import load_dotenv
from typing import Union
from aiohttp import FormData
from urllib.parse import quote
from aiohttp import ClientSession, FormData


load_dotenv()


# environment variable retrievals
TEST_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")


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


async def send_photo_via_bot(photo, chat_id, caption=None):
    """
    Sends a photo message to a specified chat via Telegram bot. The photo can be a file on the local system,
    a URL, or a file_id of a photo already uploaded to Telegram servers.

    :param photo: Local photo as an instance of UploadFile, URL, or file_id.
    :param chat_id: Unique identifier for the target chat.
    :param caption: Optional. Photo caption (may also be used when resending photos by file_id).
    """

    url = f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendPhoto"
    data = FormData()

    data.add_field("photo", photo)
    data.add_field("chat_id", str(chat_id))

    if caption:
        data.add_field("caption", caption)

    async with ClientSession() as session:
        try:
            async with session.post(url, data=data) as response:
                response_json = await response.json()
                if response_json.get("ok"):
                    return {
                        "message": "Photo sent successfully",
                        "result": response_json,
                    }
                else:
                    # Handling cases where Telegram API returns an error.
                    return {
                        "error": response_json.get(
                            "description", "Unknown error occurred"
                        )
                    }
        except Exception as e:
            return {"error": str(e)}
