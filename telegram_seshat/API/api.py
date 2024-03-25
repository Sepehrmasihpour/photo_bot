from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from bot_actions import *

load_dotenv()
app = FastAPI()


CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")
TEST_GROUP_ID = os.getenv("TEST_GROUP_ID")

# TODO: read the fast api docs for a way to efficently test the endpoints for the api
# TODO: document the functions and the why and how things are the way they are use the full capibilities of better comments for this


async def send_media(
    media_type: str, chat_id: str | int, media: UploadFile | str, caption: str = None
):
    input_media_type = media_type.lower()
    media_types = {
        "photo": {
            "acceptable_mime_types": ["image/jpeg", "image/png", "image/gif"],
        },
        "audio": {
            "acceptable_mime_types": ["audio/mpeg", "audio/ogg", "audio/wav"],
        },
        "video": {
            "acceptable_mime_types": ["video/mp4", "video/ogg", "video/webm"],
        },
        "text": {None},
    }
    if input_media_type in media_types:
        media_type_data = media_types[input_media_type]
        if type(media) == str:
            result = (
                await send_media_via_bot(
                    chat_id=chat_id,
                    media=media,
                    caption=caption,
                    media_type=input_media_type,
                )
                if caption != None
                else await send_media_via_bot(
                    chat_id=chat_id, media=media, media_type=input_media_type
                )
            )
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            return {
                "message": f"Successfully sent the {input_media_type}",
                "result": result,
            }
        else:
            acceptable_mime_types = media_type_data["acceptable_mime_types"]
            if not media.content_type in acceptable_mime_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Please upload an {input_media_type}.",
                )
            result = (
                await send_media_via_bot(
                    chat_id=chat_id,
                    media=media.file,
                    caption=caption,
                    media_type=input_media_type,
                )
                if caption != None
                else await send_media_via_bot(
                    chat_id=chat_id, media=media.file, media_type=input_media_type
                )
            )
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])

            return {
                "message": f"Successfully sent the {input_media_type}",
                "result": result,
            }

    else:
        return {"error": "wrong media type, input"}


@app.post("/sendMessage/{chat_id}/{media_type}")
async def sendMessage(
    chat_id: str | int, media_type: str, media: str | UploadFile, caption: str = None
):
    input_chat_id = chat_id
    if type(chat_id) == str:
        uniqe_chat_id = {"mainGroup": TEST_GROUP_ID, "mainChannel": TEST_CHANNEL_ID}
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
