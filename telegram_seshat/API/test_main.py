# Import necessary modules and test data
from data.data import media_test_cases, telegram_ids
from fastapi.testclient import TestClient
from main import app

# Initialize the TestClient with the FastAPI app
client = TestClient(app)


def media_test_results():
    # Load test cases and initialize result storage
    test_cases = media_test_cases
    results = []

    # Initialize placeholders for request data
    data = {}
    files = {}

    # Iterate through each test case
    for case in test_cases:

        # If media is a string, prepare data payload and make POST request
        if type(case["media"]) == str:
            data = {"media": case["media"], "caption": case["caption"]}
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                data=data,
            )
            results.append(response)
        else:
            # If media is not a string, prepare files payload for multipart/form-data
            files["media"] = case["media"]
            data["caption"] = case["caption"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                data=data,
                files=files,
            )
            results.append(response)
    return results


def expected_media_test_results():
    # Prepare expected results based on test cases
    test_cases = media_test_cases
    expected_results = []
    expected_result = {
        "result": {
            "chat": {
                "id": "",
            },
            "caption": None,
        },
    }

    # Iterate through test cases to set expected results
    for case in test_cases:
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
        try:
            assert response.status_code == 200
        except AssertionError as e:
            print(f"status_code is not 200\nError: {e}\nrespnse:{response}")
            raise AssertionError


def test_send_media_chat_id():
    # Test to ensure response chat ID matches expected chat ID
    test_results = media_results
    expected_results = media_expected_results
    for response, expected_response in zip(test_results, expected_results):
        response_json = response.json()
        try:
            assert (
                str(response_json["result"]["chat"]["id"])
                == expected_response["result"]["chat"]["id"]
            )
        except AssertionError:
            print(
                f"""test case response chat_id does not match the expected response chat_id
                \nresponse chat_id:{response_json["result"]['chat']['id']} != expected response chat_id:{expected_response["result"]['chat']['id']}
                  """
            )

            raise AssertionError


def test_send_media_caption():
    # Test to ensure response caption matches expected caption
    test_results = media_results
    expected_results = media_expected_results
    for response, expected_response in zip(test_results, expected_results):
        response_json = response.json()
        try:
            if expected_response["result"]["caption"]:
                assert (
                    response_json["result"]["caption"]
                    == expected_response["result"]["caption"]
                )
        except:
            print(
                f"""test case response caption does not match the expected response caption
                \nresponse result:{response_json["result"]} != expected response caption:{expected_response["result"]["caption"]}
                  """
            )
            raise AssertionError
