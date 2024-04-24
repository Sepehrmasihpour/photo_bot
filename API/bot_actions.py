from typing import IO
from data import telegram_ids
import httpx


BOT_TOKEN = telegram_ids["BOT_TOKEN"]


def send_media_via_bot(
    media: str | IO[any],
    media_type: str,
    chat_id: str | int,
    caption: str | None = None,
):

    media_types = ["photo", "text", "audio", "video"]  # Supported media types.
    input_media_type = media_type.lower()
    if input_media_type in media_types:
        # Constructing the request URL based on the media type.
        general_url = f"https://api.telegram.org/bot{BOT_TOKEN}/send"
        request_url = (
            f"{general_url}{input_media_type.capitalize()}"
            if input_media_type != "text"
            else f"{general_url}Message"
        )
        try:

            if type(media) == str:
                if caption:
                    response = httpx.post(
                        request_url,
                        params={"caption": caption, "chat_id": chat_id},
                        data={input_media_type: media},
                    )
                else:
                    response = httpx.post(
                        request_url,
                        params={"chat_id": chat_id},
                        data={input_media_type: media},
                    )

            else:
                response = httpx.post(
                    request_url,
                    params={"caption": caption, "chat_id": chat_id},
                    files={input_media_type: media},
                )
            response_json = response.json()
            if response_json.get("ok"):
                return response_json
            else:
                return {
                    "error": response_json.get("description", "Unknown error occurred")
                }
        except Exception as e:
            return {"error": str(e)}

    else:
        return {"error": "unacceptable media type"}
