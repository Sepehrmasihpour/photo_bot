import os
from dotenv import load_dotenv


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

uniqe_chat_ids = {
    "mainGroup": telegram_ids["GROUP_ID"],
    "mainChannel": telegram_ids["CHANNEL_ID"],
}

# * This the test data for testing send_media endpoint
media_test_cases = [
    {
        "chat_id": telegram_ids["BOT_CHAT_ID"],
        "media_type": "photo",
        "media": "https://fastly.picsum.photos/id/326/200/200.jpg?hmac=T_9V3kc7xrK46bj8WndwDhPuvpbjnAM3wfL_I7Gu6yA",  # url
        "caption": "Test photo caption",
    },
    {
        "chat_id": telegram_ids["BOT_CHAT_ID"],
        "media_type": "photo",
        "media": "AgACAgQAAx0EfU-ioAADsWYB_ebHeQOR1Wg22hYQYMAxwKhSAAJ7wTEbJysQULO2VE-EtnaVAQADAgADcwADNAQ",  # file_id
        "caption": "Test photo caption",
    },
    {
        "chat_id": telegram_ids["BOT_CHAT_ID"],
        "media_type": "audio",
        "media": "CQACAgQAAx0EfU-ioAADsmYCBRCwx7kBIWmwrASYWOy06FDhAAKmEwACJysQUEYwlN5ZdJodNAQ",  # file_id
        "caption": "Test audio caption",
    },
    {
        "chat_id": telegram_ids["BOT_CHAT_ID"],
        "media_type": "text",
        "media": "testing the sendMessage method",  # file_id
        "caption": None,
    },
]
