# This file contains Pytest-based unit tests for the Faststamps web-app-api
import pytest
from fastapi.testclient import TestClient
from main import app

# Constants
API_PORT = 8081
API_BASE_URL = "http://127.0.0.1:%s" % (API_PORT)


@pytest.fixture
def client():
    """We can't just instantiate TestClient like this:
       client = TestClient(app)
       because that will not trigger event handlers in your API app.
       See: https://fastapi.tiangolo.com/advanced/testing-events/"""
    with TestClient(app) as c:
        yield c


def test_api_root(client):
    resource = "/"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json() == {"name": "Faststamps web-app-api.",
                        "version": "0.0.1",
                        "openapi_specification": "http://127.0.0.1:8081/docs",
                        "health": "http://127.0.0.1:8081/health"}
