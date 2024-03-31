from aiohttp import FormData
from data.data import send_media_test_cases
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_send_media():
    test_cases = send_media_test_cases
    data = {}
    files = {}
    for case in test_cases:
        # Prepare data dictionary based on whether 'caption' is provided
        if type(case["media"]) == str:
            data = {"media": case["media"], "caption": case["caption"]}
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                data=data,
            )
        else:
            files["media"] = case["media"]
            data["caption"] = case["caption"]
            response = client.post(
                f"/sendMessage/{case['chat_id']}/{case['media_type']}",
                data=data,
                files=files,
            )

        # Check if the response status code is 200, print the case and fail the test if not
        try:
            assert response.status_code == 200
        except AssertionError as e:
            print(f"Test failed for case: {case}\nError: {e}")
            raise AssertionError
