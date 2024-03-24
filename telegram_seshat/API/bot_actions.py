import os
from dotenv import load_dotenv
from typing import Union, IO
from aiohttp import FormData
from urllib.parse import quote
from aiohttp import ClientSession, FormData


load_dotenv()


# environment variable retrievals
TEST_BOT_TOKEN = os.getenv("TEST_BOT_TOKEN")


# * This function sends all the none text media to the desired chat_id using the telegram API
async def send_media_via_bot(
    media: str | IO[any], media_type: str, chat_id: str | int, caption: str = None
):
    media_types = {
        "photo": {"url": f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendPhoto"},
        "text": {"url": f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendMessage"},
        "audio": {"url": f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendAudio"},
        "video": {"url": f"https://api.telegram.org/bot{TEST_BOT_TOKEN}/sendVideo"},
    }
    input_media_type = media_type.lower()
    if input_media_type in media_types:
        media_type_data = media_types[input_media_type]
        url = media_type_data["url"]
        data = FormData()

        data.add_field(input_media_type, media)
        data.add_field("chat_id", chat_id)

        if caption:
            data.add_field("caption", caption)

        async with ClientSession() as session:
            try:
                async with session.post(url, data=data) as response:
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
