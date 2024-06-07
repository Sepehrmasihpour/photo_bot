# tests/test_sendMedia.py
import pytest


def media_test_results(client, media_test_cases_fixture):
    """
    Executes media test cases and collects the responses.

    Returns:
        list: A list of responses from the API for each test case.
    """
    test_cases = media_test_cases_fixture
    results = []

    for case in test_cases:
        params = {"caption": case["caption"]}
        data = {}
        files = {}

        if isinstance(case["media"], str):
            data["media"] = case["media"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                params=params,
                data=data,
            )
        else:
            files["media"] = case["media"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                params=params,
                files=files,
            )
        results.append(response)
    return results


def expected_media_test_results(media_test_cases_fixture, telegram_ids_fixture):
    """
    Prepares the expected results based on the test cases.

    Returns:
        list: A list of expected results for each test case.
    """
    test_cases = media_test_cases_fixture
    expected_results = []

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

        if case["chat_id"] != "mainGroup" and case["chat_id"] != "mainchannel":
            expected_result["result"]["chat"]["id"] = case["chat_id"]
        else:
            if case["chat_id"] == "mainGroup":
                expected_result["result"]["chat"]["id"] = telegram_ids_fixture[
                    "GRPUP_ID"
                ]
            else:
                expected_result["result"]["chat"]["id"] = telegram_ids_fixture[
                    "CHANNEL_ID"
                ]
        expected_results.append(expected_result)
    return expected_results


@pytest.fixture(scope="module")
def media_results(client, media_test_cases_fixture):
    return media_test_results(client, media_test_cases_fixture)


@pytest.fixture(scope="module")
def media_expected_results(media_test_cases_fixture, telegram_ids_fixture):
    return expected_media_test_results(media_test_cases_fixture, telegram_ids_fixture)


def test_send_media_status(media_results):
    """
    Test to ensure each response status code is 200.

    Asserts:
        Each response from the media tests returns a status code of 200.
    """
    for response in media_results:
        response_json = response.json()
        assert (
            response.status_code == 200
        ), f"Status code is not 200\nResponse: {response_json}"


def test_send_media_chat_id(
    media_results, media_expected_results, uniqe_chat_ids_fixture
):
    """
    Test to ensure response chat ID matches expected chat ID.

    Asserts:
        Each response chat ID matches the expected chat ID.
    """
    for response, expected_response in zip(media_results, media_expected_results):
        try:
            response_json = response.json()
        except AttributeError:
            print("Error: Response does not support json method")
            continue

        chat_id_info = response_json.get("result", {}).get("chat", {})
        chat_id = chat_id_info.get("id")
        if chat_id is None:
            print("Chat ID not found in the response")
            continue

        chat_id = str(chat_id)
        expected_chat_id_info = expected_response.get("result", {}).get("chat", {})
        expected_chat_id = expected_chat_id_info.get("id")
        if expected_chat_id in uniqe_chat_ids_fixture:
            expected_chat_id = uniqe_chat_ids_fixture[expected_chat_id]

        assert (
            chat_id == expected_chat_id
        ), f"The chat ID is not as expected.\nChat ID: {chat_id}\nExpected chat ID: {expected_chat_id}"


def test_send_media_caption(media_results, media_expected_results):
    """
    Test to ensure response caption matches expected caption.

    Asserts:
        Each response caption matches the expected caption.
    """
    for response, expected_response in zip(media_results, media_expected_results):
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
