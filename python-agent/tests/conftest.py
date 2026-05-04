from fastapi.testclient import TestClient

from server import app


def pytest_sessionstart(session):  # pragma: no cover - pytest hook
    del session


def pytest_sessionfinish(session, exitstatus):  # pragma: no cover - pytest hook
    del session, exitstatus


def pytest_configure(config):  # pragma: no cover - pytest hook
    del config


import pytest


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client
