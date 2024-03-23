from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile
from bot_actions import *

load_dotenv()
app = FastAPI()


CHANNEL_ID = os.getenv("CHANNEL_ID")
GROUP_ID = os.getenv("GROUP_ID")
TEST_CHANNEL_ID = os.getenv("TEST_CHANNEL_ID")
TEST_GROUP_ID = os.getenv("TEST_GROUP_ID")


async def send_media(
    media_type: str, chat_id: str | int, media: UploadFile | str, caption: str = None
):
    input_media_type = media_type.lower()
    media_types = {
        "photo": {
            "acceptable_mime_types": ["image/jpeg", "image/png", "image/gif"],
            "bot_action": send_photo_via_bot,
        },
        "audio": {
            "acceptable_mime_types": ["audio/mpeg", "audio/ogg", "audio/wav"],
            "bot_action": send_audio_via_bot,
        },
        "video": {
            "acceptable_mime_types": ["video/mp4", "video/ogg", "video/webm"],
            "bot_action": send_video_via_bot,
        },
        "text": {"bot_action": send_message_via_bot},
    }
    if input_media_type in media_types:
        data = media_types[input_media_type]
        bot_action = data["bot_action"]
        if type(media) == str:
            result = (
                await bot_action(chat_id=chat_id, media=media, caption=caption)
                if caption != None
                else await bot_action(chat_id=chat_id, media=media)
            )
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])
            return {
                "message": f"Successfully sent the {input_media_type}",
                "result": result,
            }
        else:
            acceptable_mime_types = data["acceptable_mime_types"]
            if not media.content_type in acceptable_mime_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type. Please upload an {input_media_type}.",
                )
            result = (
                await bot_action(chat_id=chat_id, media=media.file, caption=caption)
                if caption != None
                else await bot_action(chat_id=chat_id, media=media.file)
            )
            if "error" in result:
                raise HTTPException(status_code=400, detail=result["error"])

            return {
                "message": f"Successfully sent the {input_media_type}",
                "result": result,
            }

    else:
        return {"error": "wrong media type, input"}


# the end point for sending a message via bot to a specific chatID uisng
@app.post("/sendMessage/text/{message}/{chat_id}")
async def send_message(message: str, chat_id: int | str):
    result = await send_media(chat_id=chat_id, media=message, media_type="text")
    return result


@app.post("/sendMessage/mainGroup/text/{message}")
async def message_group(message: str):
    result = await send_media(chat_id=TEST_GROUP_ID, media=message, media_type="text")
    return result


@app.post("/post/mainChannel/text/{post}")
async def post_channel(post: str):
    result = await send_media(chat_id=TEST_CHANNEL_ID, media=post, media_type="text")
    return result


# The endpoints for sendimg/posting pictures


@app.post("/sendMessage/photo")
async def send_photo(chat_id: str | int, photo: UploadFile | str, caption: str = None):
    result = await send_media(
        chat_id=chat_id, media=photo, caption=caption, media_type="photo"
    )
    return result


@app.post("/sendMessage/mainGroupn/photo")
async def send_photo_group(photo: UploadFile | str, caption: str = None):
    result = await send_media(
        chat_id=TEST_GROUP_ID, media=photo, caption=caption, media_type="photo"
    )
    return result


@app.post("/post/mainChannel/photo")
async def post_photo_channel(photo: UploadFile | str, caption: str = None):
    result = await send_media(
        chat_id=TEST_CHANNEL_ID, media=photo, caption=caption, media_type="photo"
    )
    return result


@app.post("/sendMessage/video")
async def send_video(chat_id: str | int, video: UploadFile | str, caption: str | int):
    result = await send_media(
        chat_id=chat_id, media=video, caption=caption, media_type="video"
    )
    return result
