# tests/conftest.py
import pytest
import sqlite3
from fastapi.testclient import TestClient
from create_db import create_database
from main import app
from data import (
    media_test_cases,
    uniqe_chat_ids,
    telegram_ids,
)


@pytest.fixture(scope="session")
def client():
    """
    Fixture to create a TestClient instance for the FastAPI app.

    This client is used to send HTTP requests to the API during tests.
    The scope is 'session' to ensure a single instance is used for all tests in the session.
    """
    return TestClient(app)


@pytest.fixture(scope="module")
def media_test_cases_fixture():
    """
    Fixture to provide media test cases data.

    This fixture supplies the media test cases data to the tests.
    The scope is 'module' to share the same data across all tests in a module.
    """
    return media_test_cases


@pytest.fixture(scope="module")
def uniqe_chat_ids_fixture():
    """
    Fixture to provide unique chat IDs data.

    This fixture supplies the unique chat IDs to the tests.
    The scope is 'module' to share the same data across all tests in a module.
    """
    return uniqe_chat_ids


@pytest.fixture(scope="module")
def telegram_ids_fixture():
    """
    Fixture to provide Telegram IDs data.

    This fixture supplies the Telegram IDs to the tests.
    The scope is 'module' to share the same data across all tests in a module.
    """
    return telegram_ids


@pytest.fixture(scope="session")
def db_connection():
    """
    Fixture to create a database connection.

    This fixture sets up the database by calling the create_database function,
    and then establishes a connection to the SQLite database.
    The connection is yielded to be used by the tests and closed after the session.
    """
    create_database()
    conn = sqlite3.connect("seshat_manager.db")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    """
    Fixture to set up and tear down the database state before and after each test.

    This fixture ensures the database is in a clean state before each test runs.
    It calls the create_database function to ensure the database and tables are set up,
    and deletes all records from the group_members table after each test.
    The autouse=True parameter ensures this fixture is used automatically by all tests.
    """
    create_database()
    yield
    conn = sqlite3.connect("seshat_manager.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM group_members")
    conn.commit()
    conn.close()
