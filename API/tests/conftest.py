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
    return TestClient(app)


@pytest.fixture(scope="module")
def media_test_cases_fixture():
    return media_test_cases


@pytest.fixture(scope="module")
def uniqe_chat_ids_fixture():
    return uniqe_chat_ids


@pytest.fixture(scope="module")
def telegram_ids_fixture():
    return telegram_ids


@pytest.fixture(scope="session")
def db_connection():
    create_database()
    conn = sqlite3.connect("seshat_manager.db")
    conn.row_factory = sqlite3.Row
    yield conn
    conn.close()


@pytest.fixture(scope="function", autouse=True)
def setup_and_teardown_db():
    create_database()
    yield
    conn = sqlite3.connect("seshat_manager.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM group_members")
    conn.commit()
    conn.close()
