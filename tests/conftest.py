import pytest
from fastapi.testclient import TestClient

from main import create_app


@pytest.hookimpl(optionalhook=True)
@pytest.fixture(scope="module")
def pytest_client() -> TestClient:
    return TestClient(create_app(False))
