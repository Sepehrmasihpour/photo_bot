import pytest
from fastapi.testclient import TestClient


def test_update_group_members_add_new_member(client, db_connection):
    """
    Test case to verify adding a new group member and updating the user count.

    Steps:
    1. Delete any existing member with chat_id = 1 to ensure a clean state.
    2. Fetch the initial user count.
    3. Send a POST request to add a new member with chat_id = 1.
    4. Assert that the response status code is 200.
    5. Assert that the response JSON indicates the member was added successfully.
    6. Query the database to check that the new member was correctly inserted.
    7. Assert that the queried member matches the expected name and username.
    8. Assert that the user count has increased by 1.
    """
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (1,))
    db_connection.commit()

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    initial_count = cursor.fetchone()[0]

    response = client.post(
        "/updateGroupMembers",
        json={"chat_id": 1, "name": "John Doe", "user_name": "johndoe"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Group member added successfully"}

    cursor.execute("SELECT * FROM group_members WHERE chat_id = ?", (1,))
    member = cursor.fetchone()
    assert member is not None
    assert member["name"] == "John Doe"
    assert member["user_name"] == "johndoe"

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    new_count = cursor.fetchone()[0]
    assert new_count == initial_count + 1


def test_update_group_members_update_existing_member(client, db_connection):
    """
    Test case to verify updating an existing group member.

    Steps:
    1. Delete any existing member with chat_id = 2 to ensure a clean state.
    2. Insert a new member with chat_id = 2, user_name = 'janedoe', and name = 'Jane Doe'.
    3. Commit the new member to the database.
    4. Send a POST request to update the member's name and username.
    5. Assert that the response status code is 200.
    6. Assert that the response JSON indicates the member was updated successfully.
    7. Query the database to check that the member's details were correctly updated.
    8. Assert that the queried member matches the new name and username.
    9. Assert that the user count remains unchanged.
    """
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (2,))
    db_connection.commit()

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    initial_count = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO group_members (chat_id, user_name, name) VALUES (?, ?, ?)",
        (2, "janedoe", "Jane Doe"),
    )
    db_connection.commit()

    response = client.post(
        "/updateGroupMembers",
        json={"chat_id": 2, "name": "Jane Smith", "user_name": "janesmith"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Group member updated successfully"}

    cursor.execute("SELECT * FROM group_members WHERE chat_id = ?", (2,))
    member = cursor.fetchone()
    assert member is not None
    assert member["name"] == "Jane Smith"
    assert member["user_name"] == "janesmith"

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    new_count = cursor.fetchone()[0]
    assert new_count == initial_count


def test_update_group_members_no_update_required(client, db_connection):
    """
    Test case to verify that no update occurs when the name and username are unchanged.

    Steps:
    1. Delete any existing member with chat_id = 3 to ensure a clean state.
    2. Insert a new member with chat_id = 3, user_name = 'janedoe', and name = 'Jane Doe'.
    3. Commit the new member to the database.
    4. Send a POST request with the same name and username to check no update is needed.
    5. Assert that the response status code is 200.
    6. Assert that the response JSON indicates no update was required.
    7. Query the database to check that the member's details remain unchanged.
    8. Assert that the queried member matches the original name and username.
    9. Assert that the user count remains unchanged.
    """
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (3,))
    db_connection.commit()

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    initial_count = cursor.fetchone()[0]

    cursor.execute(
        "INSERT INTO group_members (chat_id, user_name, name) VALUES (?, ?, ?)",
        (3, "janedoe", "Jane Doe"),
    )
    db_connection.commit()

    response = client.post(
        "/updateGroupMembers",
        json={"chat_id": 3, "name": "Jane Doe", "user_name": "janedoe"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "No update required as the name and username are unchanged"
    }

    cursor.execute("SELECT * FROM group_members WHERE chat_id = ?", (3,))
    member = cursor.fetchone()
    assert member is not None
    assert member["name"] == "Jane Doe"
    assert member["user_name"] == "janedoe"

    cursor.execute("SELECT count FROM user_count WHERE id = 1")
    new_count = cursor.fetchone()[0]
    assert new_count == initial_count
