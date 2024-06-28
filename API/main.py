import sqlite3
from fastapi import FastAPI, HTTPException, UploadFile
from bot_actions import *  # Importing necessary functions for bot actions.
from data import telegram_ids, uniqe_chat_ids, GroupMember

# Import the create_database function from create_db
from create_db import create_database

app = FastAPI()  # Initialize FastAPI app for creating RESTful APIs easily.

# Retrieve various chat and group IDs from environment variables for flexibility and security.
CHANNEL_ID = telegram_ids["CHANNEL_ID"]
GROUP_ID = telegram_ids["GROUP_ID"]


def get_db_connection():
    """
    Establishes and returns a connection to the 'seshat_manager.db' SQLite database.

    The row_factory attribute is set to sqlite3.Row to allow dictionary-style access to row data.
    """
    # Call the function to ensure the database exists
    create_database()
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


@app.post("/updateGroupMembers")
async def update_group_members(payload: GroupMember):
    """
    Endpoint to update the 'group_members' table in the database.

    This endpoint performs the following operations:
    1. Connects to the database.
    2. Checks if a record with the given 'chat_id' exists in the 'group_members' table.
       - If it exists and the 'name' and 'user_name' are unchanged, it returns a message indicating no update is required.
       - If it exists and either the 'name' or 'user_name' has changed, it updates the record with the new values.
       - If it does not exist, it inserts a new record with the provided 'chat_id', 'name', and 'user_name'.
    3. Commits the transaction to the database.
    4. Returns a success message indicating whether a member was added or updated.
    5. Handles any exceptions by raising an HTTP 500 error with the exception details.
    6. Ensures the database connection is closed.

    Parameters:
    - payload: A Pydantic model 'GroupMemberUpdate' containing:
      - chat_id: The chat ID of the group member (integer).
      - name: The name of the group member (string).
      - user_name: The username of the group member (string).

    Returns:
    - JSON response with a message indicating the outcome of the operation.
    """
    conn = get_db_connection()  # Connect to the database
    try:
        cursor = conn.cursor()  # Create a cursor object to execute SQL commands
        cursor.execute(
            "SELECT name, user_name FROM group_members WHERE chat_id = ?",
            (payload.chat_id,),
        )  # Check if a record with the given 'chat_id' exists
        result = cursor.fetchone()  # Fetch the result of the query
        if result:
            current_name, current_user_name = result  # Unpack the result
            if current_name == payload.name and current_user_name == payload.user_name:
                # Return a message if no update is required
                return {
                    "message": "No update required as the name and username are unchanged"
                }
            # Update the record if the 'name' or 'user_name' has changed
            cursor.execute(
                """
                UPDATE group_members
                SET user_name = ?, name = ?
                WHERE chat_id = ?
                """,
                (payload.user_name, payload.name, payload.chat_id),
            )
            conn.commit()  # Commit the changes to the database
            return {"message": "Group member updated successfully"}
        else:
            # Insert a new record if it does not exist
            cursor.execute(
                """
                INSERT INTO group_members (chat_id, user_name, name)
                VALUES (?, ?, ?)
                """,
                (payload.chat_id, payload.user_name, payload.name),
            )
            conn.commit()  # Commit the new record to the database
            return {"message": "Group member added successfully"}
    except Exception as e:
        # Raise an HTTP 500 error with the exception details in case of an error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()  # Ensure the database connection is closed


@app.delete("/removeGroupMembers")
async def remove_group_members(payload: GroupMember):
    """
    Endpoint to remove a member from the 'group_members' table in the database.

    This endpoint performs the following operations:
    1. Connects to the database.
    2. Checks if a record with the given 'chat_id' and 'user_name' exists in the 'group_members' table.
       - If it exists, deletes the record.
       - If it does not exist, returns a message indicating no such member was found.
    3. Commits the transaction to the database.
    4. Returns a success message indicating the member was removed or an error message if not found.
    5. Handles any exceptions by raising an HTTP 500 error with the exception details.
    6. Ensures the database connection is closed.

    Parameters:
    - payload: A Pydantic model 'groupMemberRemove' containing:
      - chat_id: The chat ID of the group member (integer).
      - user_name: The username of the group member (string).
      - name: The name of the group member (string, optional).

    Returns:
    - JSON response with a message indicating the outcome of the operation.
    """
    conn = get_db_connection()  # Connect to the database
    try:
        cursor = conn.cursor()  # Create a cursor object to execute SQL commands
        cursor.execute(
            "SELECT * FROM group_members WHERE chat_id = ? AND user_name = ?",
            (payload.chat_id, payload.user_name),
        )  # Check if a record with the given 'chat_id' and 'user_name' exists
        result = cursor.fetchone()  # Fetch the result of the query
        if result:
            # Delete the record if it exists
            cursor.execute(
                "DELETE FROM group_members WHERE chat_id = ? AND user_name = ?",
                (payload.chat_id, payload.user_name),
            )
            conn.commit()  # Commit the changes to the database
            return {"message": "Group member removed successfully"}
        else:
            # Return a message if no such member was found
            return {"message": "No such member found"}
    except Exception as e:
        # Raise an HTTP 500 error with the exception details in case of an error
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()  # Ensure the database connection is closed


@app.post("/changGroupPhoto")
async def change_group_photo(photo_id: str):
    pass
    # * The plan for this is to make a function at the bot_action module That will take a photo_id as the input and than
    # * it will use the getFile method of the telegram api to get the file path of the photo and than send a request to
    # * download the photo and upload its content to the db.
    # * As got what will happen on this side in the endpoint the endpoint will take the a photo_id as the param and than it will send
    # * that photo_id to the bot_actions download_photo function and than search through the db using the photo_id for the photo and than offering it as input to
    # * another function that will be made in the bot actions that is called set_chat_photo which is basicly a wrapper for the telegram api method of setChatPhoto using using
    # * photo input file as input and chat_id as param for theh function.
    # * At last we will call another function that will be made in bot_action  module this is for deleting photos from the db and having a photo_id as param.
    #! Don't forget error handling at all levels.
