import pytest
import sqlite3
from create_db import create_database
from db_modules import (
    get_db_connection,
    get_member_info,
    update_member_info,
    insert_member_info,
    delete_member_info,
    member_count_controll,
)


# Set up an in-memory SQLite database for testing
@pytest.fixture(scope="function")
def db_connection():
    # Create an in-memory database
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    # Create the necessary tables
    with conn:
        conn.execute(
            """
            CREATE TABLE group_members (
                chat_id INTEGER PRIMARY KEY,
                user_name TEXT,
                name TEXT,
                last_proposal_date TEXT
            )
        """
        )
        conn.execute(
            """
            CREATE TABLE user_count (
                id INTEGER PRIMARY KEY,
                count INTEGER
            )
        """
        )
        conn.execute("INSERT INTO user_count (id, count) VALUES (1, 0)")
    yield conn
    conn.close()


def test_get_db_connection(monkeypatch, db_connection):
    def mock_create_database():
        pass

    monkeypatch.setattr("db_modules.create_database", mock_create_database)
    monkeypatch.setattr("db_modules.sqlite3.connect", lambda _: db_connection)

    conn = get_db_connection()
    assert conn is not None


def test_insert_member_info(db_connection, monkeypatch):
    monkeypatch.setattr("db_modules.get_db_connection", lambda: db_connection)

    result = insert_member_info(1, "John Doe", "johndoe")
    assert result == True

    with db_connection:
        cursor = db_connection.execute("SELECT * FROM group_members WHERE chat_id = 1")
        row = cursor.fetchone()
        assert row["name"] == "John Doe"
        assert row["user_name"] == "johndoe"


def test_get_member_info(db_connection, monkeypatch):
    monkeypatch.setattr("db_modules.get_db_connection", lambda: db_connection)

    # Insert a test member
    with db_connection:
        db_connection.execute(
            "INSERT INTO group_members (chat_id, user_name, name) VALUES (1, 'johndoe', 'John Doe')"
        )

    member_info = get_member_info(1)
    assert member_info == {
        "name": "John Doe",
        "user_name": "johndoe",
        "last_proposal_date": None,
    }


def test_update_member_info(db_connection, monkeypatch):
    monkeypatch.setattr("db_modules.get_db_connection", lambda: db_connection)

    # Insert a test member
    with db_connection:
        db_connection.execute(
            "INSERT INTO group_members (chat_id, user_name, name) VALUES (1, 'johndoe', 'John Doe')"
        )

    result = update_member_info(1, "john_doe_updated", "John Doe Updated")
    assert result == True

    with db_connection:
        cursor = db_connection.execute("SELECT * FROM group_members WHERE chat_id = 1")
        row = cursor.fetchone()
        assert row["user_name"] == "john_doe_updated"
        assert row["name"] == "John Doe Updated"


def test_delete_member_info(db_connection, monkeypatch):
    monkeypatch.setattr("db_modules.get_db_connection", lambda: db_connection)

    # Insert a test member
    with db_connection:
        db_connection.execute(
            "INSERT INTO group_members (chat_id, user_name, name) VALUES (1, 'johndoe', 'John Doe')"
        )

    result = delete_member_info(1)
    assert result == True

    with db_connection:
        cursor = db_connection.execute("SELECT * FROM group_members WHERE chat_id = 1")
        row = cursor.fetchone()
        assert row is None


def test_member_count_controll(db_connection, monkeypatch):
    monkeypatch.setattr("db_modules.get_db_connection", lambda: db_connection)

    result = member_count_controll(add=True)
    assert result == True

    with db_connection:
        cursor = db_connection.execute("SELECT count FROM user_count WHERE id = 1")
        row = cursor.fetchone()
        assert row["count"] == 1

    result = member_count_controll(add=False)
    assert result == True

    with db_connection:
        cursor = db_connection.execute("SELECT count FROM user_count WHERE id = 1")
        row = cursor.fetchone()
        assert row["count"] == 0
