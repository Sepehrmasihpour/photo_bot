import aiohttp
import os
from dotenv import load_dotenv
from typing import Union
from aiohttp import ClientError, ClientSession
from aiofiles import open as aioopen
from os.path import exists


load_dotenv()


# environment variable retrievals
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")
TEST_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")
TEST_GROUP_ID = os.getenv("TEST_GROUP_ID")


# TODO find out why the send_message_via_bot dosent work
# TODO test the send_photo_via_bot function and is's api endPoint in main

# these are the functions that use the telegram api to send text message to pacific chat ,main group, main channel


# Asynchronously sends a message to a specified chat via the Telegram Bot API.
async def send_message_via_bot(message: str, chat_id: Union[str, int]):
    send_text = f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={message}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(send_text) as response:
                if response.status == 200:
                    return await response.json()  # Return the successful response
                else:
                    error_message = (
                        f"Error sending message: HTTP status {response.status}"
                    )
                    return {"error": error_message}
        except aiohttp.ClientError as e:
            error_message = f"Client error occurred: {e}"
        except Exception as e:  # A fallback for unexpected exceptions
            error_message = f"An unexpected error occurred: {e}"
        return {"error": error_message}  # Return the error message


# Asynchronously posts a message to the main channel under the seshat control using the Bot API.
async def send_message_channel(text_post: str):
    response = await send_message_via_bot(text_post, TEST_CHANNEL_ID)
    return response


# ! I this function dosen't work find out why and fix it
# Asynchronously sends a tex message to the main group under the seshat control using the Bot API.
async def message_group_via_bot(message: str):
    response = await send_message_via_bot(message, TEST_GROUP_ID)
    return response


# this are the functions that will use the telegram api to send/post photos to pacific chat,main group or main channel


# !test this
async def send_photo_via_bot(photo, chat_id, caption=None):
    """
    this dose the same job as the text message counterpart the only difference is in the file format of the photo it either can be
    inside the telgram servers or a internet adress or a file on the local memory each one is different thats the reson for the slight
    diffrence between this function and its counterpart
    """
    url = f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendPhoto"
    data = {"chat_id": chat_id, "caption": caption}
    files = None

    # Check if the photo parameter points to a local file
    if isinstance(photo, str) and not photo.startswith("http") and exists(photo):
        try:
            # Use aiofiles for async file handling
            async with aioopen(photo, "rb") as f:
                files = {"photo": f}
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, data=data, files=files) as response:
                        response_json = await response.json()
                        if response.status != 200:
                            raise Exception(f"Telegram API Error: {response_json}")
                        return response_json
        except Exception as e:
            print(f"Error sending photo: {e}")
            return None
    else:
        data["photo"] = photo
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data) as response:
                    response_json = await response.json()
                    if response.status != 200:
                        raise Exception(f"Telegram API Error: {response_json}")
                    return response_json
        except ClientError as e:
            print(f"Network/HTTP error occurred: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error occurred: {e}")
            return None
