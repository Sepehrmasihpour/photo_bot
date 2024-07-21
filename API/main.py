import time
from db_modules import *
from bot_actions import *  # Importing necessary functions for bot actions.
from fastapi import FastAPI, HTTPException, UploadFile
from data import telegram_ids, GroupMember
from datetime import datetime, timedelta


app = FastAPI()  # Initialize FastAPI app for creating RESTful APIs easily.

# Retrieve various chat and group IDs from environment variables for flexibility and security.
CHANNEL_ID = telegram_ids["CHANNEL_ID"]
GROUP_ID = telegram_ids["GROUP_ID"]

@app.post("/message/{media_type}")
async def messageGroup(
    media_type: str,
    media: str | UploadFile,
    chat_id:int = GROUP_ID,
    caption: str | None = None,
):
    result = send_media_via_bot(
        chat_id=chat_id,
        media=media,
        media_type=media_type,
        caption=caption,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/getUpdates")
async def getUpdates(allowed_updates: list[str] = [], offset: int = 0):
    try:
        result = telegram_getUpdates(allowed_updates=allowed_updates, offset=offset)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/updateGroupMembers")
async def update_group_members(payload: GroupMember):
    try:
        result = get_member_info(chat_id=payload.chat_id)
        if result:
            current_name, current_user_name, last_proposal_date = result  # Unpack the result
            if current_name == payload.name and current_user_name == payload.user_name:
                # Return a message if no update is required
                return {
                    "message": "No update required as the name and username are unchanged"
                }
            # Update the record if the 'name' or 'user_name' has changed
            update_member_info(name=payload.name, user_name=payload.user_name, chat_id=payload.chat_id)
            return {"message": "Group member updated successfully"}
        else:
            insert_member_info(chat_id=payload.chat_id,name=payload.name,user_name=payload.user_name)# Insert a new record if it does not exist
            member_count_controll()# Update the user count
            return {"message": "Group member added successfully"}
    except Exception as e:
        # Raise an HTTP 500 error with the exception details in case of an error
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/removeGroupMembers")
async def remove_group_members(payload: GroupMember):
    try:
        result = get_member_info(chat_id=payload.chat_id)
        if result:
            # Delete the record if it exists
            delete_member_info(chat_id=payload.chat_id)
            # Update the user count
            member_count_controll(add=False)
            return {"message": "Group member removed successfully"}
        else:
            # Return a message if no such member was found
            return {"message": "No such member found"}
    except Exception as e:
        # Raise an HTTP 500 error with the exception details in case of an error
        raise HTTPException(status_code=500, detail=str(e))


@app.post(
"/changeGroupPhoto") 
async def change_group_photo(file_id: str):
    try:
        result = set_chat_photo(file_id=file_id, chat_id=GROUP_ID)
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/voteGroupPhoto")
async def vote_group_photo(
    chat_id: int | str, argument: str, photo_file_id: str, anonymous: bool
):
    conn = get_db_connection()
    cursor = conn.cursor()  # Create a cursor object to execute SQL commands
    cursor.execute(
        "SELECT name, user_name, last_proposal_date FROM group_members WHERE chat_id = ?",
        (chat_id),
    )  # Check if a record with the given 'chat_id' exists
    result = cursor.fetchone()  # Fetch the result of the query
    if result:
        name, user_name, last_proposal_date = result
        current_time = datetime.now()
        if last_proposal_date == None or (current_time - datetime.strptime(last_proposal_date, "%Y-%m-%d %H:%M:%S")) > timedelta(hours=24):
            cursor.execute("SELECT is_active from votes_in_progress WHERE vote_type = 'group_photo'")
            vote_in_progress = True if cursor.fetchone()[0] == 0 else False
            if vote_in_progress:
                raise HTTPException(
                    status_code=500, detail=f"There can be only one active proposal for the same issue at the same time"
                )
            else:
                post_photo_response = send_media_via_bot(
                media=photo_file_id,
                media_type="photo",
                chat_id=telegram_ids["GROUP_ID"],
                caption="This is the photo that is being proposed to be replace the current group photo",
            )
                if post_photo_response.get("ok"):
                    pass
                    #! after this post the poll for changing the group photo and run it for 24h or until 3/4 of the group vote unless the group member count is 5 or less 
                    #! in that case run it for 24h or until all member vote after uset the postPoll and poll result and stop poll to do this and while loop and sleep functions 
                    #! and depending on the final function either do nothind other than sending a message to the group that the proposal has not been approvedn or change the photo 
                    #! using the setChatPhoto function 
                    #! P.S depending on the anonymous param make sure to either mention the member who proposed this or not0
                else:
                    raise HTTPException(
                        status_code=500, detail=f"failed to post the photo on the group \ndetails: {post_photo_response.get("error")}"
                    )

        else:
            raise HTTPException(
                status_code=500,
                detail="Every member can only suggest a proposal for the group once every 24 hours",
            )
    else:
        raise HTTPException(
            status_code=500,
            detail="The chat_id provided is not in the group  data_base",
        )
