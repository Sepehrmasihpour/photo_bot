# tests/test_getUpdate.py
import pytest
from bot_actions import send_media_via_bot


def getUpdate_results(client, offset=None, selected_updates=None):
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
        response.raise_for_status()
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


def recive_test_updates(
    client, telegram_ids_fixture, offset=None, selected_updates=None
):
    """
    Sends 4 test messages of various media types to the test channel to generate updates for testing.

    Args:
        offset (int, optional): Identifier of the first update to be returned.
        selected_updates (list[str], optional): List of update types to retrieve.

    Returns:
        dict: JSON response containing updates if successful, otherwise None.
    """
    test_param = True
    chat_id_param = telegram_ids_fixture["TEST_CHANNEL_ID"]
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
    return getUpdate_results(client, offset=offset, selected_updates=selected_updates)


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


def test_getUpdate_status(client):
    """
    Test if getUpdate_status correctly identifies a successful response.

    Asserts:
        The getUpdate method successfully fetches updates and the response is valid.
    """
    response = getUpdate_results(client)
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


def test_getUpdates_offset(client, telegram_ids_fixture):
    """
    Test if the offset parameter works correctly with the getUpdates method.

    Asserts:
        The offset parameter correctly handles the updates and the method fetches new updates properly.
    """
    response = getUpdate_results(client)
    assert response is not None, "Failed to fetch updates"
    assert getUpdate_status(
        response
    ), "getUpdate method did not return a successful response."

    if not enough_updates(response):
        response = recive_test_updates(client, telegram_ids_fixture)

    highest_update_id = get_highest_updateId(response)
    assert highest_update_id is not None, "No updates found"

    recive_test_updates(client, telegram_ids_fixture, offset=highest_update_id + 1)
    new_response = getUpdate_results(client)
    assert new_response is not None, "Failed to fetch new updates"

    lowest_updateId = get_highest_updateId(new_response, maximum=False)
    assert lowest_updateId is not None, "No new updates found"
    assert lowest_updateId > highest_update_id, "The offset parameter is not working."
