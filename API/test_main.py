# Import necessary modules and test params
#! This import dosent work inside the tests/endpoints directory find out why and fix it\
import time
from fastapi.testclient import TestClient
from main import app
from bot_actions import send_media_via_bot
from data import (
    media_test_cases,
    uniqe_chat_ids,
    telegram_ids,
)


# !Initialize the TestClient with the FastAPI app
client = TestClient(app)

# !ERROR:there is no test for sending local files in to the api

#! -------------------------------------------------------sendMedia-----------------------------------------------

# * The below section is for the sendMedia method.


def media_test_results():
    # Load test cases and initialize result storage
    test_cases = media_test_cases
    results = []

    # Iterate through each test case
    for case in test_cases:
        # Initialize placeholders for request data
        params = {"caption": case["caption"]}
        data = {}
        files = {}
        # If media is a string, prepare params payload and make POST request
        if type(case["media"]) == str:
            data["media"] = case["media"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                params=params,
                data=data,
            )
            results.append(response)
        else:
            # If media is not a string, prepare files payload for multipart/form-
            files["media"] = case["media"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                params=params,
                files=files,
            )
            results.append(response)
    return results


def expected_media_test_results():
    # Prepare expected results based on test cases
    test_cases = media_test_cases
    expected_results = []

    # Iterate through test cases to set expected results
    for case in test_cases:
        expected_result = {
            "result": {
                "chat": {
                    "id": "",
                },
                "caption": None,
            },
        }
        if case["caption"]:
            expected_result["result"]["caption"] = case["caption"]

        # Check for specific chat IDs and adjust accordingly
        if case["chat_id"] != "mainGroup" or "mainchannel":
            expected_result["result"]["chat"]["id"] = case["chat_id"]
        else:
            if case["chat_id"] == "mainGroup":
                expected_result["result"]["chat"]["id"] = telegram_ids["GRPUP_ID"]
            else:
                expected_result["result"]["chat"]["id"] = telegram_ids["CHANNEL_ID"]
        expected_results.append(expected_result)
    return expected_results


# Execute the tests and store results
media_results = media_test_results()
media_expected_results = expected_media_test_results()


def test_send_media_status():
    # Test to ensure each response status code is 200
    test_results = media_results
    for response in test_results:
        response_json = response.json
        assert (
            response.status_code == 200
        ), f"status_code is not 200\nrespnse:{response_json}"


def test_send_media_chat_id():
    # Test to ensure response chat ID matches expected chat ID
    results = media_results
    expected_results = media_expected_results
    for response, expected_response in zip(results, expected_results):
        try:
            response_json = response.json()
        except AttributeError:
            print("Error: Response does not support json method")
            continue

        # Safer access to nested dictionary keys
        chat_id_info = response_json.get("result", {}).get("chat", {})
        chat_id = chat_id_info.get("id")
        if chat_id is None:
            print("Chat ID not found in the response")
            continue

        # Convert to string and check conditions
        chat_id = str(chat_id)
        # Access expected chat ID safely
        expected_chat_id_info = expected_response.get("result", {}).get("chat", {})
        expected_chat_id = expected_chat_id_info.get("id")
        if expected_chat_id in uniqe_chat_ids:
            expected_chat_id = uniqe_chat_ids[expected_chat_id]
        # Assert condition
        assert (
            chat_id == expected_chat_id
        ), f"The chat ID is not as expected.\nchat ID: {chat_id}\nexpected chat ID: {expected_chat_id}"


def test_send_media_caption():
    # Test to ensure response caption matches expected caption
    results = media_results
    expected_results = media_expected_results
    for response, expected_response in zip(results, expected_results):
        try:
            response_json = response.json()
        except AttributeError:
            print("Error: Response does not support json method")
            continue

        expected_caption = expected_response.get("result", {}).get("caption")
        caption = response_json.get("result", {}).get("caption", None)

        if expected_caption is not None:
            assert caption is not None, f"The caption is missing."
            assert (
                caption == expected_caption
            ), f"The caption is not as expected.\nResponse caption: {caption}\nExpected caption: {expected_caption}"
        else:
            assert caption is None, f"Expected no caption, but got: {caption}"


#! -------------------------------------------------------getUpdate-----------------------------------------------

# *The below section is for the getUpdates method.


# the data needed for the getUpdates tests
def getUpdate_results(
    offset: int | None = None, selected_updates: list[str] | None = None
):
    """
    Retrieves updates from the Telegram API.

    Returns:
        dict: JSON response containing updates.
            Returns None if there's an error fetching updates.
    """
    try:
        params = {}
        if offset is not None:
            params["offset"] = offset
        if selected_updates is not None:
            params["selected_updates"] = selected_updates

        response = client.get("/getUpdates", params=params)
        response.raise_for_status()  # Ensure the request was successful
        return response.json()
    except Exception as e:
        print(f"Error fetching updates: {e}")
        return None


getUpdate_response_json = getUpdate_results()
getUpdate_response_results = getUpdate_response_json["result"]


def getUpdate_status():
    """
    sees if the getUpdate method recives an ok call back from the api or 200
    """
    response = getUpdate_response_json
    if response and response["ok"] == True:
        return True
    return False


def recive_test_updates(
    offset: int | None = None, selected_udpates: list[str] | None = None
):
    """
    This funciton will send 4 messages of various media types to the test group that the bot can recive updates.
    This funcitn should be used where there are not enough updates to do tests on.
    It uses the send_medi_via_bot function in the bot_actions file.
    """
    global getUpdate_response_json
    global getUpdate_response_results

    test_param = True
    chat_id_param = telegram_ids["BOT_CHAT_ID"]
    media_type_params = ["text", "photo", "audio", "text"]
    media_params = [
        "test_user text message",
        "https://fastly.picsum.photos/id/326/200/200.jpg?hmac=T_9V3kc7xrK46bj8WndwDhPuvpbjnAM3wfL_I7Gu6yA",
        "CQACAgQAAx0EfU-ioAADsmYCBRCwx7kBIWmwrASYWOy06FDhAAKmEwACJysQUEYwlN5ZdJodNAQ",
        "test_user text message(2)",
    ]
    caption_params = [None, "Test_user photo message", "test_user audio message", None]
    for i in range(4):
        send_media_via_bot(
            media=media_params[i],
            media_type=media_type_params[i],
            caption=caption_params[i],
            chat_id=chat_id_param,
            test=test_param,
        )
    getUpdate_response_json = getUpdate_results(
        offset=offset, selected_updates=selected_udpates
    )
    getUpdate_response_results = getUpdate_response_json["result"]


def get_highest_updateId(maximum: bool = True):
    update_result = getUpdate_response_results
    highest_updateId = (
        max(update["update_id"] for update in update_result)
        if maximum
        else min(update["update_id"] for update in update_result)
    )
    return highest_updateId


def test_getUpdate_status():
    status = getUpdate_status()
    assert (
        status
    ), f"getUpdate method has a failed called,\ngetUpdate method response : {getUpdate_response_json}"


def enough_updates():
    updates_result = getUpdate_response_results
    update_result_numbers = len(updates_result)
    if not updates_result:
        return False
    if update_result_numbers < 4:
        return False
    return True


def ask_user_for_updates(
    offset: int | None = None, selected_updates: list[str] | None = None
):
    global getUpdate_response_json
    global getUpdate_response_results
    print(
        "please send atleast 4 messages of any kind to the bot\n I will wait for 30 seconds for you, if you don't do this we will set the test as a faillure"
    )
    time.sleep(20)
    getUpdate_response_json = getUpdate_results(
        offset=offset, selected_updates=selected_updates
    )
    getUpdate_response_results = getUpdate_response_json["result"]


def test_getUpdates_offset():
    status = getUpdate_status()
    if not status:
        assert (
            status
        ), "because of the not ok status of the method This test cannot be excuted"
    good_update_number = enough_updates()
    if not good_update_number:
        ask_user_for_updates()
    good_update_number = enough_updates()
    if not good_update_number:
        assert good_update_number, "there are not enough updates for the tests"
    highest_update_id = get_highest_updateId()
    ask_user_for_updates(offset=highest_update_id + 1)
    good_update_number = enough_updates()
    if not good_update_number:
        assert good_update_number, "there are not enough updates for the tests"
    lowest_updateId = get_highest_updateId(maximum=False)
    assert lowest_updateId > highest_update_id, "The offset param is not working"
