from typing import Union, Annotated
from fastapi import FastAPI, HTTPException
from bot_actions import *


app = FastAPI()


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
    result = await message_group_via_bot(message)
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
    result = await send_message_channel(post)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {
        "message": "Successfully posted the text message",
        "result": result,
    }


# The endpoints for sendimg/posting pictures


# !This function local file photo dose not work fix it later
@app.post("/sendMessage/photo/{chat_id}")
async def send_photo_endpoint(
    photo: str, chat_id: Union[int, str], caption: str | None = None
):
    result = await send_photo_via_bot(photo=photo, chat_id=chat_id, caption=caption)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
