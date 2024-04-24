# Import necessary modules and test params
#! This import dosent work inside the tests/endpoints directory find out why and fix it\
from data import (
    media_test_cases,
    uniqe_chat_ids,
    telegram_ids,
)
from fastapi.testclient import TestClient
from main import app


# !Initialize the TestClient with the FastAPI app
client = TestClient(app)

# !ERROR:there is no test for sending local files in to the api


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
