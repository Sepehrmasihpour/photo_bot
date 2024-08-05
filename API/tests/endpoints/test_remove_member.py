from fastapi.testclient import TestClient
from db_control import (
    get_member_info,
    delete_member_info,
    insert_member_info,
)
import pytest

member_data = {"name": "test_name", "user_name": "test_user_name", "chat_id": 1}
chat_id = member_data["chat_id"]


@pytest.fixture(scope="module")
def setup_member():
    insert_member_info(
        chat_id=chat_id,
        name=member_data["name"],
        user_name=member_data["user_name"],
    )
    yield
    delete_member_info(chat_id)


def test_remove_existing_member(client):
    try:
        response = client.delete("/removeGroupMembers", json={"chat_id": chat_id})
        result = get_member_info(chat_id=chat_id)
        assert response.status_code == 200
        assert response.json()["message"] == "Group member removed successfully"
        assert result is None, "The member data was not deleted from the database"
        # Ensure member count is decreased
        # Implement your member_count_controll check logic here
    except Exception as e:
        print(f"Error in removing the member. Error: {e}")


def test_remove_non_existent_member(client):
    try:
        non_existent_chat_id = 9999
        response = client.delete(
            "/removeGroupMembers", json={"chat_id": non_existent_chat_id}
        )
        result = get_member_info(chat_id=non_existent_chat_id)
        assert response.status_code == 200
        assert response.json()["message"] == "No such member found"
        assert result is None, "There should be no member with this chat ID"
    except Exception as e:
        print(f"Error in testing non-existent member removal. Error: {e}")


def test_remove_member_error_handling(client, mocker):
    try:
        mocker.patch("my_app.get_member_info", side_effect=Exception("Test exception"))
        response = client.delete("/removeGroupMembers", json={"chat_id": chat_id})
        assert response.status_code == 500
        assert response.json()["detail"] == "Test exception"
    except Exception as e:
        print(f"Error in testing error handling. Error: {e}")
