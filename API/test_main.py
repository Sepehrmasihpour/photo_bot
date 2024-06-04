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
    """
    Executes media test cases and collects the responses.

    Returns:
        list: A list of responses from the API for each test case.
    """
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
        if isinstance(case["media"], str):
            data["media"] = case["media"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                params=params,
                data=data,
            )
        else:
            # If media is not a string, prepare files payload for multipart/form-data
            files["media"] = case["media"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                params=params,
                files=files,
            )
        results.append(response)
    return results


def expected_media_test_results():
    """
    Prepares the expected results based on the test cases.

    Returns:
        list: A list of expected results for each test case.
    """
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
        if case["chat_id"] != "mainGroup" and case["chat_id"] != "mainchannel":
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
    """
    Test to ensure each response status code is 200.

    Asserts:
        Each response from the media tests returns a status code of 200.
    """
    test_results = media_results
    for response in test_results:
        response_json = response.json
        assert (
            response.status_code == 200
        ), f"Status code is not 200\nResponse: {response_json}"


def test_send_media_chat_id():
    """
    Test to ensure response chat ID matches expected chat ID.

    Asserts:
        Each response chat ID matches the expected chat ID.
    """
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
        ), f"The chat ID is not as expected.\nChat ID: {chat_id}\nExpected chat ID: {expected_chat_id}"


def test_send_media_caption():
    """
    Test to ensure response caption matches expected caption.

    Asserts:
        Each response caption matches the expected caption.
    """
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
            assert caption is not None, "The caption is missing."
            assert (
                caption == expected_caption
            ), f"The caption is not as expected.\nResponse caption: {caption}\nExpected caption: {expected_caption}"
        else:
            assert caption is None, f"Expected no caption, but got: {caption}"


#! -------------------------------------------------------getUpdate-----------------------------------------------


def getUpdate_results(offset=None, selected_updates=None):
    """
    Retrieves updates from the Telegram API.

    Args:
        offset (int, optional): Identifier of the first update to be returned. Pass offset to retrieve updates
                                starting from a specific point in time.
        selected_updates (list[str], optional): List of update types to retrieve. For example, ['message', 'edited_message'].

    Returns:
        dict: JSON response containing updates if successful, otherwise None.
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


def getUpdate_status(getUpdate_results):
    """
    Checks if the getUpdate method receives a successful response.

    Args:
        getUpdate_results (dict): The result from getUpdate_results function.

    Returns:
        bool: True if the response is successful and contains "ok": True, otherwise False.
    """
    return getUpdate_results and getUpdate_results.get("ok", False)


def recive_test_updates(offset=None, selected_updates=None):
    """
    Sends 4 test messages of various media types to the test channel to generate updates for testing.

    Args:
        offset (int, optional): Identifier of the first update to be returned.
        selected_updates (list[str], optional): List of update types to retrieve.

    Returns:
        dict: JSON response containing updates if successful, otherwise None.
    """
    test_param = True
    chat_id_param = telegram_ids["TEST_CHANNEL_ID"]
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
    return getUpdate_results(offset=offset, selected_updates=selected_updates)


def get_highest_updateId(getUpdate_response, maximum=True):
    """
    Retrieves the highest or lowest update ID from the response.

    Args:
        getUpdate_response (dict): The result from getUpdate_results function.
        maximum (bool, optional): If True, returns the highest update ID, otherwise the lowest. Defaults to True.

    Returns:
        int: The highest or lowest update ID, depending on the maximum parameter, or None if no updates are found.
    """
    update_result = getUpdate_response.get("result", [])
    if not update_result:
        return None
    return (
        max(update["update_id"] for update in update_result)
        if maximum
        else min(update["update_id"] for update in update_result)
    )


def test_getUpdate_status():
    """
    Test if getUpdate_status correctly identifies a successful response.

    Asserts:
        The getUpdate method successfully fetches updates and the response is valid.
    """
    response = getUpdate_results()
    assert response is not None, "Failed to fetch updates"
    assert getUpdate_status(response), "getUpdate method failed."


def enough_updates(getUpdate_response):
    """
    Checks if there are enough updates for testing.

    Args:
        getUpdate_response (dict): The result from getUpdate_results function.

    Returns:
        bool: True if there are at least 4 updates, otherwise False.
    """
    updates_result = getUpdate_response.get("result", [])
    return len(updates_result) >= 4


def test_getUpdates_offset():
    """
    Test if the offset parameter works correctly with the getUpdates method.

    Asserts:
        The offset parameter correctly handles the updates and the method fetches new updates properly.
    """
    response = getUpdate_results()
    assert response is not None, "Failed to fetch updates"
    assert getUpdate_status(
        response
    ), "getUpdate method did not return a successful response."

    if not enough_updates(response):
        response = recive_test_updates()

    highest_update_id = get_highest_updateId(response)
    assert highest_update_id is not None, "No updates found"

    recive_test_updates(offset=highest_update_id + 1)
    new_response = getUpdate_results()
    assert new_response is not None, "Failed to fetch new updates"

    lowest_updateId = get_highest_updateId(new_response, maximum=False)
    assert lowest_updateId is not None, "No new updates found"
    assert lowest_updateId > highest_update_id, "The offset parameter is not working."


# *The below will be for testing the selected_updates param of the getUpdates method
