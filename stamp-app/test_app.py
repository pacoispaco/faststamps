# This file contains Pytest-based unit tests for the Faststamps app
import pytest
from fastapi.testclient import TestClient
from main import app


# Constants
API_PORT = 8008
API_BASE_URL = "http://127.0.0.1:%s" % (API_PORT)
FAVICON_FILE = "favicon.png"
FASTSTAMPS_LOGO_FILE = "faststamps-logo.png"
FASTSTAMPS_JS_FILE = "faststamps.js"


@pytest.fixture
def client():
    """We can't just instantiate TestClient like this:
       client = TestClient(app)
       because that will not trigger event handlers in your API app.
       See: https://fastapi.tiangolo.com/advanced/testing-events/"""
    with TestClient(app) as c:
        yield c


def test_app_index(client):
    resource = "/"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "server-timing" in r.headers


def test_app_assets(client):
    resource = "/favicon.png"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "server-timing" in r.headers
    with open(FAVICON_FILE, 'rb') as f:
        data = f.read()
    assert r.read() == data

    resource = "/faststamps-logo.png"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "server-timing" in r.headers
    with open(FASTSTAMPS_LOGO_FILE, 'rb') as f:
        data = f.read()

    resource = "/faststamps.js"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "server-timing" in r.headers
    with open(FASTSTAMPS_JS_FILE, 'rb') as f:
        data = f.read()
