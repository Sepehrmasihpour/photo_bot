from dotenv import load_dotenv
from typing import Union
from fastapi import FastAPI, HTTPException, UploadFile
from bot_actions import *

load_dotenv()
app = FastAPI()


CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")
TEST_GROUP_ID = os.getenv("TEST_GROUP_ID")


# the end point for sending a message via bot to a specific chatID uisng
# the send_message_via_bot function
@app.post("/sendMessage/text/{message}/{chat_id}")
async def send_message(message: str, chat_id: Union[int, str]):
    result = await send_message_via_bot(message, chat_id)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "message": "Successfully sent the message",
        "result": result,
    }


# this endpoint will send text message to the main group under the sehsat control
# uisng the message_group_via_bot function
@app.post("/sendMessage/mainGroup/text/{message}")
async def message_group(message: str):
    result = await send_message_via_bot(message, TEST_GROUP_ID)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "message": "Successfult sent the message to the main group",
        "result": result,
    }


# this endpoint will post a text message to the main channel under the sehsat control
# using the send_message_channel function
@app.post("/post/mainChannel/text/{post}")
async def post_channel(post: str):
    result = await send_message_via_bot(post, TEST_CHANNEL_ID)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "message": "Successfully posted the text message",
        "result": result,
    }


# The endpoints for sendimg/posting pictures


@app.post("/sendMessage/photo/{chat_id}")
async def send_photo(chat_id: str, photo: Union[UploadFile, str], caption: str = None):
    # List of acceptable MIME types for photos
    acceptable_mime_types = ["image/jpeg", "image/png", "image/gif"]

    # Check if uploaded photo is a string or a file and if its a file weather its MIME type is acceptable
    if type(photo) == str:
        result = await send_photo_via_bot(photo=photo, chat_id=chat_id, caption=caption)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return {
            "message": "Successfully sent the Photo",
            "result": result,
        }

    else:
        if photo.content_type not in acceptable_mime_types:
            raise HTTPException(
                status_code=400, detail="Unsupported file type. Please upload an image."
            )

        # send the photo_data to the telegram api
        result = await send_photo_via_bot(
            photo=photo.file, chat_id=chat_id, caption=caption
        )
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return {
            "message": "Successfully sent the Photo",
            "result": result,
        }


@app.post("/sendMessage/mainGroupn/photo")
async def send_photo_group(photo: Union[UploadFile, str], caption: str | None = None):
    result = await send_photo(photo=photo, chat_id=TEST_GROUP_ID, caption=caption)
    return {
        "message": "Successfully sent the Photo to the main group",
        "result": result,
    }


@app.post("/post/mainChannel/photo")
async def post_photo_channel(photo: Union[UploadFile, str], caption: str | None = None):
    result = await send_photo(photo=photo, chat_id=TEST_CHANNEL_ID, caption=caption)
    return {
        "message": "Successfully posted the Photo to the main channel",
        "result": result,
    }
