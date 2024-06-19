import pytest
from fastapi.testclient import TestClient


def test_update_group_members_add_new_member(client, db_connection):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (1,))
    db_connection.commit()

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


def test_update_group_members_update_existing_member(client, db_connection):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (2,))
    db_connection.commit()

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


def test_update_group_members_no_update_required(client, db_connection):
    cursor = db_connection.cursor()
    cursor.execute("DELETE FROM group_members WHERE chat_id = ?", (3,))
    db_connection.commit()

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
