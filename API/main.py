from fastapi import FastAPI, HTTPException, UploadFile
from bot_actions import *  # Importing necessary functions for bot actions.
from data import telegram_ids

app = FastAPI()  # ! Initialize FastAPI app for creating RESTful APIs easily.

#! The Caption param is dying in one of the places it's passing find out which, print output of each of the checkpoints insted of passing them.
#! rewrite all the pointless conditonal variables. The type control in the param will do the trick.


# Retrieve various chat and group IDs from environment variables for flexibility and security.
CHANNEL_ID = telegram_ids["CHANNEL_ID"]
GROUP_ID = telegram_ids["GROUP_ID"]


async def send_media(
    media_type: str,
    chat_id: str | int,
    media: UploadFile | str,
    caption: str | None,
):
    """
    Asynchronously sends different types of media to a specified chat using a bot.

    Supports sending media like photos, audio, video, and text by calling the `send_media_via_bot` function.
    Validates the media type and its MIME type before sending to ensure compatibility.

    Parameters:
    - media_type: Type of the media (photo, audio, video, text).
    - chat_id: The chat ID where the media will be sent. Accepts both string and integer values.
    - media: The media to be sent, can be a path (str) or an uploaded file (UploadFile).
    - caption: Optional caption for the media.

    Returns:
    - A dictionary with a success message and result on success, or raises HTTPException on failure.
    """

    input_media_type = media_type.lower()
    media_types = {
        "photo": {"acceptable_mime_types": ["image/jpeg", "image/png", "image/gif"]},
        "audio": {"acceptable_mime_types": ["audio/mpeg", "audio/ogg", "audio/wav"]},
        "video": {"acceptable_mime_types": ["video/mp4", "video/ogg", "video/webm"]},
        "text": {None},
    }
    if input_media_type in media_types:
        media_type_data = media_types[input_media_type]
        if type(media) == str:
            # Directly send media if it's a string (path or URL).
            result = await send_media_via_bot(
                chat_id=chat_id,
                media=media,
                caption=caption,
                media_type=input_media_type,
            )
            # Error handling.
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            return result
        else:
            # Validate MIME type for uploaded files.
            acceptable_mime_types = media_type_data["acceptable_mime_types"]
            if media.content_type not in acceptable_mime_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Please upload an {input_media_type}.",
                )
            # Sending media file after validation.
            result = await send_media_via_bot(
                chat_id=chat_id,
                media=media.file,
                caption=caption,
                media_type=input_media_type,
            )
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])

            return result

    else:
        return {"error": "wrong media type, input"}


@app.post("/sendMessage/{chat_id}/{media_type}")
async def sendMessage(
    chat_id: str | int,
    media_type: str,
    media: str | UploadFile,
    caption: str | None = None,
):
    """
    Endpoint to send media messages to specific chat IDs via HTTP POST request.

    It leverages `send_media` function to perform the action, supporting dynamic chat ID resolution for convenience.

    Parameters mirror `send_media` function, with the addition of handling special chat ID mappings.
    """

    input_chat_id = chat_id  # Handling dynamic chat ID resolution.
    if type(chat_id) == str:
        uniqe_chat_id = {"mainGroup": GROUP_ID, "mainChannel": CHANNEL_ID}
        input_chat_id = uniqe_chat_id[chat_id] if chat_id in uniqe_chat_id else chat_id
    result = await send_media(
        chat_id=input_chat_id,
        media=media,
        media_type=media_type,
        caption=caption,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
