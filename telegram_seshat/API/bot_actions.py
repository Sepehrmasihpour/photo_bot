import os
from dotenv import load_dotenv
from typing import IO
from aiohttp import FormData
from aiohttp import ClientSession, FormData


load_dotenv()


# environment variable retrievals
TEST_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")


# TODO: document the functions and the why and how things are the way they are use the full capibilities of better comments for this


async def send_media_via_bot(
    media: str | IO[any], media_type: str, chat_id: str | int, caption: str = None
):
    media_types = ["photo", "text", "audio", "video"]
    input_media_type = media_type.lower()
    if input_media_type in media_types:
        general_url = f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/send"
        request_url = (
            f"{general_url}{input_media_type.capitalize()}"
            if input_media_type is not "text"
            else f"{general_url}Message"
        )
        data = FormData()

        data.add_field(input_media_type, media)
        data.add_field("chat_id", chat_id)

        if caption:
            data.add_field("caption", caption)

        async with ClientSession() as session:
            try:
                async with session.post(request_url, data=data) as response:
                    response_json = await response.json()
                    if response_json.get("ok"):
                        return {
                            "message": f"{input_media_type} sent successfully",
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
    else:
        return {"error": "unacceptable media type"}
