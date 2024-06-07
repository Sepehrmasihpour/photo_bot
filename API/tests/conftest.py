# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
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
