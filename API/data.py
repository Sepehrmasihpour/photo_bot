import os
from dotenv import load_dotenv
from pydantic import BaseModel


load_dotenv()  # ! Load environment variables for configuration purposes.

# * The general data that the telegram bot and the api uses.
telegram_ids = {
    # THese IDs are for when the app is not in production and are for testing
    "CHANNEL_ID": os.getenv("TEST_CHANNEL_ID"),
    "GROUP_ID": os.getenv("TEST_GROUP_ID"),
    "BOT_TOKEN": os.getenv("TEST_BOT_TOKEN"),
    "BOT_CHAT_ID": os.getenv("TEST_BOT_CHAT_ID"),
    # These IDs are for when the app is in production and should be switched out with the real use case
    # "CHANNEL_ID": os.getenv("CHANNEL_ID"),
    # "GROUP_ID ": os.getenv("GROUP_ID"),
    # "BOT_TOKEN": os.getenv("BOT_TOKEN"),
    # "BOT_CHAT_ID": os.getenv("BOT_CHAT_ID")
    #! the below id's are for testing the API in deployment they should not be deleted in any circumstance
    "TEST_USER_BOT_TOKEN": os.getenv("TEST_USER_BOT_TOKEN"),
    "TEST_CHANNEL_ID": os.getenv("TEST_CHANNEL_ID"),
}


class GroupMember(
    BaseModel
):  # * This is the data input type for when the api will want to do something with the group_members in the data base.
    chat_id: int
    name: str
    user_name: str
