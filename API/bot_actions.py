from typing import IO
from data import telegram_ids
import httpx
from typing import Optional, Dict, Any
import sqlite3
import requests


# Extracting the BOT_TOKEN from the data module.
BOT_TOKEN = telegram_ids["BOT_TOKEN"]
TEST_USER_BOT_TOKEN = telegram_ids["TEST_USER_BOT_TOKEN"]


# ! make a function for sneding telegram requests geres otherwise it will be repeated over and over again
#! make it so that it will have a request argument with the type string and basicly use the logic in the send_media_via_bot function to make it


def telegram_api_request(
    request: str,
    method: str = "GET",
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    files: Optional[Dict[str, Any]] = None,
    test_user: bool = False,
):
    url = (
        f"https://api.telegram.org/bot{BOT_TOKEN}/{request}"
        if not test_user
        else f"https://api.telegram.org/bot{TEST_USER_BOT_TOKEN}/{request}"
    )
    try:
        if method.upper() == "POST":
            response = httpx.post(url, params=params, data=data, files=files)
        else:
            response = httpx.get(url, params=params)
        response.raise_for_status()  # Ensure any HTTP errors raise an exception
        response_json = response.json()
        return response_json
    except httpx.RequestError as e:
        print(f"An error occurred while making the request: {e}")
        return {"ok": False, "error": str(e)}
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.text}")
        return {"ok": False, "error": e.response.text}
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"ok": False, "error": str(e)}


def send_media_via_bot(
    media: str | IO[any],
    media_type: str,
    chat_id: str | int,
    caption: str | None = None,
    test: bool = False,  #!This is only for testing and should it will change the default sender of the message from the to another bot. (test_purposes only)
):
    try:
        # List of supported media types
        media_types = ["photo", "text", "audio", "video"]

        # Converting the input media type to lowercase
        input_media_type = media_type.lower()

        # Checking if the input media type is valid
        if input_media_type in media_types:
            # Constructing the request URL based on the media type.
            request = (
                f"send{input_media_type.capitalize()}"
                if input_media_type != "text"
                else f"sendMessage"
            )
            data = {"chat_id": chat_id}
            files = None

            if input_media_type != "text":
                if isinstance(media, str):  # Assuming media as URL or file_id
                    data[input_media_type] = media
                else:  # Assuming media is an opened file
                    files = {input_media_type: media}
            else:
                data["text"] = (
                    media  # In case of text, the message content goes directly into data
                )

            if caption:
                data["caption"] = caption

            # Make the API request
            response = (
                telegram_api_request(request, "POST", data=data, files=files)
                if not test
                else telegram_api_request(
                    request, "POST", data=data, files=files, test_user=True
                )
            )

            if response.get("ok"):
                return response  # Return the successful response
            else:
                print(f"Failed to send media: {response.get('error')}")
                return {"ok": False, "error": response.get("error")}

        else:
            # Returning error response for unsupported media type
            return {"error": "unacceptable media type"}

    except Exception as e:
        print(f"An error occurred while sending media: {e}")
        return {"ok": False, "error": str(e)}


def telegram_getUpdates(allowed_updates: list = [], offset: int = 0):
    try:
        request = "getUpdates"
        params = {"allowed_updates": allowed_updates, "offset": offset}
        response = telegram_api_request(request=request, params=params)

        if response.get("ok"):
            return response  # Return the successful response
        else:
            print(f"Failed to get updates: {response.get('error')}")
            return {"ok": False, "error": response.get("error")}

    except Exception as e:
        print(f"An error occurred while getting updates: {e}")
        return {"ok": False, "error": str(e)}


def store_photo_path(file_id: str):
    try:
        # Step 1: Get the file info using the Telegram API.
        file_info = telegram_api_request(
            "getFile", method="GET", params={"file_id": file_id}
        )

        if file_info.get("ok"):
            photo_path = file_info["result"]["file_path"]

            # Step 2: Construct the download URL
            download_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo_path}"

            # Step 3: Store file info in the database
            db_path = "seshat_manager.db"  # Path to the SQLite database file
            conn = sqlite3.connect(db_path)  # Connect to the SQLite database
            cursor = conn.cursor()  # Create a cursor object to execute SQL commands

            cursor.execute(
                "INSERT OR REPLACE INTO photos (file_id, file_path) VALUES (?, ?)",
                (file_id, download_url),
            )
            conn.commit()  # Commit the changes to the database
            conn.close()  # Close the database connection

            return download_url  # Return the download URL
        else:
            error_message = file_info.get("error", "Unknown error")
            print(f"Failed to get file info: {error_message}")
            return None  # Return None if the file info retrieval failed

    except Exception as e:
        print(f"An error occurred while storing the photo path: {e}")
        return None  # Return None if any exception occurs


def delete_photo_path(file_id: str):
    try:
        # Step 1: Define the path to the SQLite database
        db_path = "seshat_manager.db"  # Path to the SQLite database file

        # Step 2: Connect to the SQLite database
        conn = sqlite3.connect(db_path)  # Connect to the SQLite database

        # Step 3: Create a cursor object to execute SQL commands
        cursor = conn.cursor()  # Create a cursor object to execute SQL commands

        # Step 4: Execute the DELETE statement to remove the file information
        cursor.execute("DELETE FROM photos WHERE file_id = ?", (file_id,))

        # Step 5: Commit the changes to the database
        conn.commit()  # Commit the changes to the database

        # Step 6: Close the database connection
        conn.close()  # Close the database connection

        return {"ok": True, "message": "Photo path deleted successfully"}

    except Exception as e:
        print(f"An error occurred while deleting the photo path: {e}")
        return {"ok": False, "error": str(e)}


def set_chat_photo(chat_id: str, file_id: str):
    try:
        # Step 1: Store photo path in the database and get the download URL
        file_path = store_photo_path(file_id)
        if not file_path:
            return {
                "ok": False,
                "error": "Failed to retrieve file info or store photo path",
            }

        # Step 2: Download the photo
        response = requests.get(file_path)
        if response.status_code != 200:
            return {
                "ok": False,
                "error": f"Failed to download the file: {response.status_code}",
            }

        # Step 3: Prepare the payload for setting the chat photo
        request = "setChatPhoto"
        payload = {"chat_id": chat_id}
        files = {"photo": ("photo.jpg", response.content)}

        # Step 4: Make the API request to set the chat photo
        api_response = telegram_api_request(
            request=request, method="POST", data=payload, files=files
        )

        if api_response.get("ok"):
            delete_photo_path(file_id=file_id)
            return api_response  # Return the successful response
        else:
            error_message = api_response.get("description", "Unknown error")
            if "PHOTO_CROP_SIZE_SMALL" in error_message:
                error_message = "The photo size is not within the acceptable limits (160x160 to 2048x2048 pixels)."
            print(f"Failed to set chat photo: {error_message}")
            return {"ok": False, "error": error_message}

    except Exception as e:
        print(f"An error occurred while setting the chat photo: {e}")
        return {"ok": False, "error": str(e)}


def post_poll(question: str, options: list[str], is_anonymous: bool):
    request = "sendPoll"
    method = "POST"
    params = {
        "chat_id": telegram_ids["GROUP_ID"],
        "question": question,
        "options": options,
        "is_anonymous": is_anonymous,
    }
    try:
        response = telegram_api_request(request=request, method=method, params=params)
        return response
    except Exception as e:
        return {"ok": False, "error": str(e)}


def get_poll_results(message_id):
    try:
        response = telegram_api_request(
            request="getPollResults",
            params={"chat_id": telegram_ids["GROUP_ID"], "message_id": message_id},
        )
        return response
    except Exception as e:
        return {"ok": False, "error": str(e)}


def stop_poll(message_id):
    try:
        request = "stopPoll"
        params = {"chat_id": telegram_ids["GROUP_ID"], "message_id": message_id}
        response = telegram_api_request(method="POST", request=request, params=params)
        return response
    except Exception as e:
        return {"ok": False, "error": str(e)}
