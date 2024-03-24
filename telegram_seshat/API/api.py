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


# the end point for sending a message via bot to a specific chatID uisng
@app.post("/sendMessage/text/")
async def send_message(text: str, chat_id: int | str):
    result = await send_media(chat_id=chat_id, media=text, media_type="text")
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


@app.post("/sendMessage/mainGroup/video")
async def send_video_group(video: UploadFile | str, caption: str = None):
    result = await send_media(
        chat_id=TEST_GROUP_ID, media=video, caption=caption, media_type="video"
    )
    return result


@app.post("/post/mainChannel/video")
async def post_video_channel(viedo: UploadFile | str, caption: str = None):
    result = await send_media(
        media=viedo, caption=caption, media_type="video", chat_id=TEST_CHANNEL_ID
    )
    return result


@app.post("/sendMessage/audio")
async def send_audio(chat_id: str | int, audio: UploadFile | str, caption: str | int):
    result = await send_media(
        chat_id=chat_id, media=audio, caption=caption, media_type="audio"
    )
    return result


@app.post("/sendMessage/mainGroup/audio")
async def send_audio_group(audio: UploadFile | str, caption: str = None):
    result = await send_media(
        chat_id=TEST_GROUP_ID, media=audio, caption=caption, media_type="audio"
    )
    return result


@app.post("/post/mainChannel/audio")
async def post_audio_channel(viedo: UploadFile | str, caption: str = None):
    result = await send_media(
        media=viedo, caption=caption, media_type="audio", chat_id=TEST_CHANNEL_ID
    )
    return result
