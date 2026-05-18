import pytest
from fastapi.testclient import TestClient

from api_rowboat.app.main import app


@pytest.fixture
def client():
    return TestClient(app)
