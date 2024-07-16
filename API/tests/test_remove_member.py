import pytest
from fastapi.testclient import TestClient


def test_remove_group_members_existing_member(client, db_connection):
    """
    Test case to verify removing an existing group member and updating the user count.

    Steps:
    1. Delete any existing member with chat_id = 1 to ensure a clean state.
    2. Insert a new member with chat_id = 1, user_name = 'johndoe', and name = 'John Doe'.
    3. Commit the new member to the database.
    4. Fetch the initial user count.
    5. Send a DELETE request to remove the member.
    6. Assert that the response status code is 200.
    7. Assert that the response JSON indicates the member was removed successfully.
    8. Query the database to check that the member was removed.
    9. Assert that the queried member is None.
    10. Assert that the user count has decreased by 1.
    """
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (1,))
    db_connection.commit()

    cursor.execute(
        "INSERT INTO group_members (chat_id, user_name, name) VALUES (?, ?, ?)",
        (1, "johndoe", "John Doe"),
    )
    db_connection.commit()

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    initial_count = cursor.fetchone()[0]

    response = client.request(
        "DELETE",
        "/removeGroupMembers",
        json={"chat_id": 1, "user_name": "johndoe", "name": "John Doe"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Group member removed successfully"}

    cursor.execute("SELECT * FROM group_members WHERE chat_id = ?", (1,))
    member = cursor.fetchone()
    assert member is None

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    new_count = cursor.fetchone()[0]
    assert new_count == initial_count - 1


def test_remove_group_members_nonexistent_member(client, db_connection):
    """
    Test case to verify attempting to remove a non-existent group member.

    Steps:
    1. Delete any existing member with chat_id = 2 to ensure a clean state.
    2. Fetch the initial user count.
    3. Send a DELETE request to remove a non-existent member with chat_id = 2.
    4. Assert that the response status code is 200.
    5. Assert that the response JSON indicates no such member was found.
    6. Assert that the user count remains unchanged.
    """
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (2,))
    db_connection.commit()

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    initial_count = cursor.fetchone()[0]

    response = client.request(
        "DELETE",
        "/removeGroupMembers",
        json={"chat_id": 2, "user_name": "janedoe", "name": "Jane Doe"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "No such member found"}

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    new_count = cursor.fetchone()[0]
    assert new_count == initial_count


def test_remove_group_members_invalid_payload(client):
    """
    Test case to verify handling of invalid payloads.

    Steps:
    1. Send a DELETE request with an invalid payload (missing user_name).
    2. Assert that the response status code is 422 (Unprocessable Entity).
    3. Assert that the response JSON contains validation errors.
    """
    response = client.request(
        "DELETE", "/removeGroupMembers", json={"chat_id": 3, "name": "Jane Doe"}
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    assert any(
        error["loc"] == ["body", "user_name"] for error in response.json()["detail"]
    )
