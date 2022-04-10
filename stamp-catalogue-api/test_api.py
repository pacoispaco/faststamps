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
    #print("\nSetup: Start Uvicorn with API at %s" % API_BASE_URL)
    cmd = "uvicorn main:app --reload --port=%d" % API_PORT
    p = subprocess.Popen(cmd.split(), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    yield "api"
    #print("\nTeardown: Stop Uvicorn with API at %s" % API_BASE_URL)
    p.terminate()


def test_api_root(api):
    url = '%s%s' % (API_BASE_URL, "/")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json() == {'name': 'Faststamps Catalogue API.',
                        'version': '0.0.1',
                        'openapi-specification': 'http://127.0.0.1:8888/docs',
                        'health': 'http://127.0.0.1:8888/health',
                        'resources': {}}


def test_api_stamps(api):
    url = '%s%s' % (API_BASE_URL, "/stamps")
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamps.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamps_filter_title(api):
    url = '%s%s' % (API_BASE_URL, "/stamps?title=Ceres")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 117


def test_api_stamps_filter_year(api):
    url = '%s%s' % (API_BASE_URL, "/stamps?year=1931,1932,1933")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 80


def test_api_stamps_filter_color(api):
    url = '%s%s' % (API_BASE_URL, "/stamps?color=Green,Olive")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 185


def test_api_stamps_filter_value(api):
    url = '%s%s' % (API_BASE_URL, "/stamps?value=1 French centime")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 36


def test_api_stamps_filter_stamp_type(api):
    url = '%s%s' % (API_BASE_URL, "/stamps?stamp_type=timbre")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 3770


def test_api_stamps_combined_filter(api):
    url = '%s%s' % (API_BASE_URL, "/stamps?title=Ceres&year=1850,1870,1872&color=Green,Olive&value=1 French centime&stamp_type=timbre")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_api_stamps_1a(api):
    url = '%s%s' % (API_BASE_URL, "/stamps/1a")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json() == {'yt': '1a',
                        'issued': 1850,
                        'title': 'Ceres',
                        'value': '10 French centime',
                        'color': 'Bistre brown',
                        'type': 'timbre'}


def test_api_stamps_not_found(api):
    url = '%s%s' % (API_BASE_URL, "/stamps/0")
    r = requests.get(url)
    assert r.status_code == 404
    assert r.json() == None


def test_api_stamp_titles(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_titles")
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_titles.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamp_titles_wildcard_search(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_titles?q=*")
    r = requests.get(url)
    assert r.status_code == 200
    wildcard_count = 3226
    assert r.json()["count"] == wildcard_count
    url = '%s%s' % (API_BASE_URL, "/stamp_titles")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == wildcard_count


def test_api_stamp_titles_prefix_search(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_titles?q=Ce*")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 53
    assert [title.startswith("Ce") for title in r.json()["stamp_titles"]]


def test_api_stamp_titles_suffix_search(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_titles?q=*nt")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 20
    assert [title.endswith("nt") for title in r.json()["stamp_titles"]]


def test_api_stamp_titles_infix_search(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_titles?q=C*s")
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 52
    assert [title.startswith("C") and title.endswith("s") for title in r.json()["stamp_titles"]]


def test_api_stamp_titles_wildcard_search_multiple_stars(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_titles?q=**")
    r = requests.get(url)
    assert r.status_code == 400
    assert r.json() == "Multiple wildcard stars '*' in query is not supported."


def test_api_stamp_years(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_years")
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_years.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamp_colors(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_colors")
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_colors.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamp_values(api):
    url = '%s%s' % (API_BASE_URL, "/stamp_values")
    r = requests.get(url)
    assert r.status_code == 200
    with open("test-data/stamp_values.json") as f:
        data = json.load(f)
    assert r.json() == data
