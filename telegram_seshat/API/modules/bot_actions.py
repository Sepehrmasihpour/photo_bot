from typing import IO
from aiohttp import FormData
from aiohttp import ClientSession, FormData
from data.data import telegram_ids


BOT_TOKEN = telegram_ids["BOT_TOKEN"]


async def send_media_via_bot(
    media: str | IO[any],
    media_type: str,
    chat_id: str | int,
    caption: str | None = None,
):
    """
    Asynchronously sends media to a specified chat using a Telegram bot.

    Utilizes aiohttp for asynchronous HTTP requests to the Telegram API.
    Supports different media types including photo, text, audio, and video.

    Parameters:
    - media: A string or IO type containing the media to send. Could be a file path or file-like object.
    - media_type: Type of media to send. Accepted values are "photo", "text", "audio", or "video".
    - chat_id: ID of the chat to send the media to. Can be either a string or an integer.
    - caption: Optional. Caption for the media if applicable.

    Returns:
    - A dictionary with a message and result upon success, or an error description upon failure.
    """

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
        data = FormData()

        data.add_field(input_media_type, media)  # Adding media to the FormData.
        data.add_field("chat_id", chat_id)  # Specifying the chat_id in the FormData.

        if caption:
            data.add_field(
                "caption", caption
            )  # Optional: Adding a caption if provided.

        # Asynchronous request to send the media via Telegram API.
        async with ClientSession() as session:
            try:
                async with session.post(request_url, data=data) as response:
                    response_json = await response.json()
                    if response_json.get("ok"):
                        # Successful API call.
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
                # Catching any exceptions that occur during the API call.
                return {"error": str(e)}
    else:
        # If the provided media_type is not supported.
        return {"error": "unacceptable media type"}
