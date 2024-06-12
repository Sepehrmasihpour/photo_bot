import sqlite3
from fastapi import FastAPI, HTTPException, UploadFile
from bot_actions import *  # Importing necessary functions for bot actions.
from data import telegram_ids, uniqe_chat_ids
from datetime import datetime, timedelta

app = FastAPI()  # Initialize FastAPI app for creating RESTful APIs easily.

# Retrieve various chat and group IDs from environment variables for flexibility and security.
CHANNEL_ID = telegram_ids["CHANNEL_ID"]
GROUP_ID = telegram_ids["GROUP_ID"]


def get_db_connection():
    """
    Establishes and returns a connection to the 'seshat_manager.db' SQLite database.

    The row_factory attribute is set to sqlite3.Row to allow dictionary-style access to row data.
    """
    conn = sqlite3.connect("seshat_manager.db")
    conn.row_factory = sqlite3.Row
    return conn


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
            result = send_media_via_bot(
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
            result = send_media_via_bot(
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


def uniqe_id_identifier(chat_id: str | int):
    """
    Resolves the unique ID for the given chat ID.

    If the chat ID is a string, it maps to a unique chat ID from the `uniqe_chat_ids` dictionary.
    If the chat ID is not found in the dictionary, it returns the original chat ID.

    Parameters:
    - chat_id: The chat ID to be resolved. Can be a string or integer.

    Returns:
    - The resolved chat ID.
    """
    input_chat_id = chat_id  # Handling dynamic chat ID resolution.
    if type(chat_id) == str:
        uniqe_chat_id = uniqe_chat_ids
        input_chat_id = uniqe_chat_id[chat_id] if chat_id in uniqe_chat_id else chat_id
    return input_chat_id


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
    input_chat_id = uniqe_id_identifier(chat_id)
    result = await send_media(
        chat_id=input_chat_id,
        media=media,
        media_type=media_type,
        caption=caption,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/getUpdates")
async def getUpdates(allowed_updates: list[str] = [], offset: int = 0):
    """
    Endpoint to get updates from the bot.

    Parameters:
    - allowed_updates: List of allowed update types to be retrieved.
    - offset: Offset for retrieving updates.

    Returns:
    - The result from `telegram_getUpdates` function.
    """
    result = telegram_getUpdates(allowed_updates=allowed_updates, offset=offset)
    return result


@app.post("/updateGroupMembers")  #! make some test for this
async def update_group_members(chat_id: int, name: str, user_name: str):
    """
    Endpoint to update the `group_members` table in the database.

    Checks if a record with the given `chat_id` exists. If it does and the last update was more than 5 hours ago,
    it updates the record. Otherwise, it inserts a new record.

    Parameters:
    - chat_id: The chat ID of the group member.
    - name: The name of the group member.
    - user_name: The username of the group member.

    Returns:
    - A success message or an appropriate message if no update is required.
    """
    conn = get_db_connection()
    try:
        cursur = conn.cursor()

        # Check if the chat_id exists
        cursur.execute("SELECT * FROM group_members WHERE chat_id = ?", (chat_id,))
        result = cursur.fetchone()

        if result:
            last_updated = datetime.strptime(
                result["last_updated"], "%Y-%m-%d %H:%M:%S"
            )
            current_time = datetime.now()

            # Check if the last update was more than 5 hours ago
            if current_time - last_updated > timedelta(hours=5):
                # Update the record with new user_name and name
                cursur.execute(
                    """
                    UPDATE group_members
                    SET user_name = ?, name = ?, last_updated = CURRENT_TIMESTAMP
                    WHERE chat_id = ?
                    """,
                    (user_name, name, chat_id),
                )
                conn.commit()
                return {"message": "Group member updated successfully"}
            else:
                return {
                    "message": "Update not required, last update was less than 5 hours ago"
                }
        else:
            # If not exists, insert new record
            cursur.execute(
                """
                INSERT INTO group_members (chat_id, user_name, name)
                VALUES (?, ?, ?)
                """,
                (chat_id, user_name, name),
            )
            conn.commit()
            return {"message": "Group member added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()
