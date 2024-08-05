import time
from db_control import *
from bot_actions import *  # Importing necessary functions for bot actions.
from fastapi import FastAPI, HTTPException, UploadFile
from data import telegram_ids, GroupMember
from datetime import datetime, timedelta


app = FastAPI()  # Initialize FastAPI app for creating RESTful APIs easily.

# Retrieve various chat and group IDs from environment variables for flexibility and security.
CHANNEL_ID = telegram_ids["CHANNEL_ID"]
GROUP_ID = telegram_ids["GROUP_ID"]


@app.post("/message/{media_type}")
async def message(
    media_type: str,
    media: str | UploadFile,
    chat_id: int = GROUP_ID,
    caption: str | None = None,
):
    member_info = send_media_via_bot(
        chat_id=chat_id,
        media=media,
        media_type=media_type,
        caption=caption,
    )
    if "error" in member_info:
        raise HTTPException(status_code=400, detail=member_info["error"])
    return member_info


@app.get("/getUpdates")
async def getUpdates(allowed_updates: list[str] = [], offset: int = 0):
    try:
        member_info = telegram_getUpdates(allowed_updates=allowed_updates, offset=offset)
        if "error" in member_info:
            raise HTTPException(status_code=400, detail=member_info["error"])
        return member_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/updateGroupMembers")
async def update_group_members(payload: GroupMember):
    try:
        member_info = get_member_info(chat_id=payload.chat_id)
        if member_info:
            current_name, current_user_name, last_proposal_date = (
                member_info  # Unpack the member_info
            )
            if current_name == payload.name and current_user_name == payload.user_name:
                # Return a message if no update is required
                return {
                    "message": "No update required as the name and username are unchanged"
                }
            # Update the record if the 'name' or 'user_name' has changed
            update_member_info(
                name=payload.name, user_name=payload.user_name, chat_id=payload.chat_id
            )
            return {"message": "Group member updated successfully"}
        else:
            insert_member_info(
                chat_id=payload.chat_id, name=payload.name, user_name=payload.user_name
            )  # Insert a new record if it does not exist
            member_count_controll()  # Update the user count
            return {"message": "Group member added successfully"}
    except Exception as e:
        # Raise an HTTP 500 error with the exception details in case of an error
        raise HTTPException(status_code=500, detail=str(e))

#!write tests for the updated version
@app.delete("/removeGroupMembers")
async def remove_group_members(payload: GroupMember):
    try:
        member_info = get_member_info(chat_id=payload.chat_id)
        if member_info:
            kick_member_reponse = kick_member(chat_id=GROUP_ID, user_id=payload.chat_id)
            if kick_member_reponse["ok"]:    
                # Delete the record if it exists
                delete_member_info(chat_id=payload.chat_id)
                # Update the user count
                member_count_controll(add=False)
                return {"message": "Group member removed successfully"}
            else:
                return {"ok":False, "message":f"could not kick the nmember from the group detail:{kick_member_reponse["error"]}"}
        else:
            # Return a message if no such member was found
            return {"message": "No such member found"}
    except Exception as e:
        # Raise an HTTP 500 error with the exception details in case of an error
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/changeGroupPhoto")
async def change_group_photo(file_id: str):
    try:
        member_info = set_chat_photo(file_id=file_id, chat_id=GROUP_ID)
        if "error" in member_info:
            raise HTTPException(status_code=400, detail=member_info["error"])
        return member_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# * The vote for group photo change and all the functions related to it


def is_more_than_24_hours(date: str):
    last_proposal_datetime = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.now()
    return (current_time - last_proposal_datetime) > timedelta(hours=24)

def eligble_to_suggest(chat_id:int, vote_type:str):
    response = {
        "ok":bool,
        "detail":str,
    }
    try:

        # Check if a record with the given 'chat_id' exists
        member_info = get_member_info(chat_id=chat_id)
        if not member_info:
            response["ok"] = False
            response["detail"] = "The chat_id provided is not in the group members data_base "
            return response

        last_proposal_date = member_info["last_proposal_date"]
        if last_proposal_date != None or not is_more_than_24_hours(last_proposal_date):
            response["ok"] = False
            response["detail"] = "Every member can only suggest a proposal for the group once every 24 hours"
            return response

        vote_in_progress = is_vote_active(vote_type=vote_type)
        if vote_in_progress:
            response["ok"] = False
            response["detail"] = "there is currently a voet on the same subject in progress. there can only be one at a time"
            return response
        
    except Exception as e:
        response['ok'] = False
        response["detail"] = f"{e}"
        
    

@app.post("/voteGroupPhoto")
async def vote_group_photo(
    chat_id: int | str, argument: str, photo_file_id: str, anonymous: bool
):
    allowed_to_suggest = eligble_to_suggest(chat_id=chat_id, vote_type="group_photo")
    if not allowed_to_suggest["ok"] :
        raise HTTPException(status_code=400, detail=allowed_to_suggest["detail"])

    post_photo_response = message(
    media=photo_file_id,
    media_type="photo",
    caption="This is the photo that is being proposed to replace the current group photo",
)
    if not post_photo_response.get("ok"):
        raise HTTPException(
            status_code=400, detail=f"failed to post the photo on the group \ndetails: {post_photo_response.get("error")}"
        )
    needed_info = get_member_info(chat_id=chat_id) if not anonymous else None
    if anonymous:
        poll_question = f"The member who has suggested this change wants to remain anonymous{argument}"
    else:
        poll_question = f"{needed_info["user_name"]} member has suggested this change\n{argument}"
    post_poll_result = post_poll(options=["YES", "NO"], question=poll_question)
    if not post_poll_result['ok']:
        raise HTTPException(status_code=400, detail= f"we could not post the poll to the group \ndetail: {post_poll_result["error"]}")
    
    poll_start_time = datetime.now()
    end_poll_time = poll_start_time + timedelta(hours=24)

    while datetime.now() < end_poll_time:
        if is_vote_active(vote_type="group_photo"):
            return {"ok":True,"message":"The voting has The voting ended succsesfully"}
        print("the vote is still active checking again in 30 second")
        time.sleep(30)
    
    return {"ok": True, "message":"after 24 hours not enough members have voted the suggestion will not go to actions"}


