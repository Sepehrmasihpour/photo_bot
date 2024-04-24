from typing import IO
from data import telegram_ids
import httpx

# Extracting the BOT_TOKEN from the data module.
BOT_TOKEN = telegram_ids["BOT_TOKEN"]


def send_media_via_bot(
    media: str | IO[any],
    media_type: str,
    chat_id: str | int,
    caption: str | None = None,
):
    """
    Sends media (photo, audio, video) or text message via Telegram bot.

    Args:
        media (str or IO[any]): The media content to be sent. It can be a file_id,url(str) or an opened file (IO[any]).
        media_type (str): The type of media to be sent. It should be one of: 'photo', 'audio', 'video', 'text'.
        chat_id (str or int): The ID of the Telegram chat where the media will be sent.
        caption (str, optional): Caption for the media (only applicable for photo, audio, video). Defaults to None.

    Returns:
        dict: A dictionary containing the response from the Telegram API.
              If the request is successful, the response will contain the sent message data.
              If an error occurs, the response will contain an 'error' key with a description of the error.

    Raises:
        None

    Note:
        This function uses the httpx library to make HTTP requests to the Telegram Bot API.

    Example:
        # Sending a photo with caption
        response = send_media_via_bot("path/to/photo.jpg", "photo", 123456, caption="Check this out!")
        print(response)
    """

    # List of supported media types
    media_types = ["photo", "text", "audio", "video"]

    # Converting the input media type to lowercase
    input_media_type = media_type.lower()

    # Checking if the input media type is valid
    if input_media_type in media_types:
        # Constructing the request URL based on the media type.
        general_url = f"https://api.telegram.org/bot{BOT_TOKEN}/send"
        request_url = (
            f"{general_url}{input_media_type.capitalize()}"
            if input_media_type != "text"
            else f"{general_url}Message"
        )

        try:
            # Handling different types of media content
            if type(media) == str:
                # If media is a file path
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
                # If media is an opened file
                response = httpx.post(
                    request_url,
                    params={"caption": caption, "chat_id": chat_id},
                    files={input_media_type: media},
                )

            # Parsing the response JSON
            response_json = response.json()

            # Checking if the request was successful
            if response_json.get("ok"):
                return response_json
            else:
                # Returning error response if request failed
                return {
                    "error": response_json.get("description", "Unknown error occurred")
                }
        except Exception as e:
            # Returning error response if an exception occurred during request
            return {"error": str(e)}

    else:
        # Returning error response for unsupported media type
        return {"error": "unacceptable media type"}
