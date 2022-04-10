# This file contains Pytest-based unit tests for the Faststamps Catalogue API
import pytest
import subprocess
import time
import requests
import json


# Constants
API_PORT = 8888
API_BASE_URL = "http://127.0.0.1:%s" % (API_PORT)


# Pid of the uvicorn process running the API
uvicorn_api_pid = None


@pytest.fixture(scope="module")
def api():
    cmd = "uvicorn main:app --reload --port=%d" % API_PORT
    # print("\nSetup: Start Uvicorn with API at %s" % API_BASE_URL)
    p = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    yield "api"
    # print("\nTeardown: Stop Uvicorn with API at %s" % API_BASE_URL)
    p.terminate()


def test_api_root(api):
    resource = "/"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json() == {'name': 'Faststamps Catalogue API.',
                        'version': '0.0.1',
                        'openapi-specification': 'http://127.0.0.1:8888/docs',
                        'health': 'http://127.0.0.1:8888/health',
                        'resources': {}}


def test_api_stamps(api):
    resource = "/stamps"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamps.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamps_filter_title(api):
    resource = ("/stamps"
                "?title=Ceres")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 117


def test_api_stamps_filter_year(api):
    resource = ("/stamps"
                "?year=1931,1932,1933")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 80


def test_api_stamps_filter_color(api):
    resource = ("/stamps"
                "?color=Green,Olive")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 185


def test_api_stamps_filter_value(api):
    resource = ("/stamps"
                "?value=1 French centime")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 36


def test_api_stamps_filter_stamp_type(api):
    resource = ("/stamps"
                "?stamp_type=timbre")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 3770


def test_api_stamps_combined_filter(api):
    resource = ("/stamps"
                "?title=Ceres"
                "&year=1850,1870,1872"
                "&color=Green,Olive"
                "&value=1 French centime"
                "&stamp_type=timbre")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_api_stamps_1a(api):
    resource = "/stamps/1a"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json() == {'yt': '1a',
                        'issued': 1850,
                        'title': 'Ceres',
                        'value': '10 French centime',
                        'color': 'Bistre brown',
                        'type': 'timbre'}


def test_api_stamps_not_found(api):
    resource = "/stamps/0"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 404
    assert r.json() is None


def test_api_stamp_titles(api):
    resource = "/stamp_titles"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_titles.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamp_titles_wildcard_search(api):
    resource = ("/stamp_titles"
                "?q=*")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    wildcard_count = 3226
    assert r.json()["count"] == wildcard_count
    url = '%s%s' % (API_BASE_URL, "/stamp_titles")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == wildcard_count


def test_api_stamp_titles_prefix_search(api):
    resource = ("/stamp_titles"
                "?q=Ce*")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 53
    assert [title.startswith("Ce") for title in r.json()["stamp_titles"]]


def test_api_stamp_titles_suffix_search(api):
    resource = ("/stamp_titles"
                "?q=*nt")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 20
    assert [title.endswith("nt") for title in r.json()["stamp_titles"]]


def test_api_stamp_titles_infix_search(api):
    resource = ("/stamp_titles"
                "?q=C*s")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 52
    assert [title.startswith("C") and title.endswith("s") for title in r.json()["stamp_titles"]]


def test_api_stamp_titles_wildcard_search_multiple_stars(api):
    resource = ("/stamp_titles"
                "?q=**")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 400
    assert r.json() == "Multiple wildcard stars '*' in query is not supported."


def test_api_stamp_years(api):
    resource = "/stamp_years"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_years.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamp_colors(api):
    resource = "/stamp_colors"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_colors.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamp_values(api):
    resource = "/stamp_values"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_values.json") as f:
        data = json.load(f)
    assert r.json() == data
