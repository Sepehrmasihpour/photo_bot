import os
from dotenv import load_dotenv
from io import BytesIO


load_dotenv()  # ! Load environment variables for configuration purposes.

# * The general data that the telegram bot and the api uses.
telegram_ids = {
    # THese IDs are for when the app is not in production and are for testing
    "CHANNEL_ID": os.getenv("TEST_CHANNEL_ID"),
    "GROUP_ID": os.getenv("TEST_GROUP_ID"),
    "BOT_TOKEN": os.getenv("TEST_BOT_TOKEN"),
    # These IDs are for when the app is in production and should be switched out with the real use case
    # "CHANNEL_ID": os.getenv("CHANNEL_ID"),
    # "GROUP_ID ": os.getenv("GROUP_ID"),
    # "BOT_TOKEN": os.getenv("BOT_TOKEN"),
}

# * This the test data for testing send_media endpoint
send_media_test_cases = [
    {
        "chat_id": "mainGroup",
        "media_type": "photo",
        "media": "https://fastly.picsum.photos/id/326/200/200.jpg?hmac=T_9V3kc7xrK46bj8WndwDhPuvpbjnAM3wfL_I7Gu6yA",  # url
        "caption": "Test photo caption",
    },
    {
        "chat_id": telegram_ids["GROUP_ID"],
        "media_type": "photo",
        "media": "AgACAgQAAx0EfU-ioAADsWYB_ebHeQOR1Wg22hYQYMAxwKhSAAJ7wTEbJysQULO2VE-EtnaVAQADAgADcwADNAQ",  # file_id
        "caption": "Test photo caption",
    },
    {
        "chat_id": "mainGroup",
        "media_type": "audio",
        "media": "CQACAgQAAx0EfU-ioAADsmYCBRCwx7kBIWmwrASYWOy06FDhAAKmEwACJysQUEYwlN5ZdJodNAQ",  # file_id
        "caption": "Test audio caption",
    },
    {
        "chat_id": telegram_ids["GROUP_ID"],
        "media_type": "text",
        "media": "testing the sendMessage method",  # file_id
        "caption": None,
    },
]
