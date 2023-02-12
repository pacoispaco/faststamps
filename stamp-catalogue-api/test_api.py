# This file contains Pytest-based unit tests for the Faststamps Catalogue API
import pytest
import subprocess
import time
import requests
import json


# Constants
API_PORT = 8008
API_BASE_URL = "http://127.0.0.1:%s" % (API_PORT)
STAMPS_TEST_DATA_FILE = "test-data/stamps.json"


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
                        'openapi-specification': f'{API_BASE_URL}/docs',
                        'health': f'{API_BASE_URL}/health',
                        'resources': {}}


def test_api_stamps(api):
    resource = "/stamps"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    with open(STAMPS_TEST_DATA_FILE) as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamps_bad_start_and_count(api):
    resource = "/stamps?start=-1"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 400
    resource = "/stamps?count=-1"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 400


def test_api_stamps_filter_title(api):
    resource = ("/stamps"
                "?title=Ceres")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 116


def test_api_stamps_filter_year(api):
    resource = ("/stamps"
                "?issued=1931,1932,1933")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 54


def test_api_stamps_filter_color(api):
    resource = ("/stamps"
                "?color=Green,Olive")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 90


def test_api_stamps_filter_value(api):
    resource = ("/stamps"
                "?value=1 French centime")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 32


def test_api_stamps_filter_stamp_type(api):
    resource = ("/stamps"
                "?stamp-type=Pour la poste Aérienne")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 127


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

def test_api_stamps_poste_1(api):
    resource = "/stamps/Poste-1"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json() == {'color-en': 'Yellow bistre',
 'color-fr': 'bistre-jaune',
 'description-fr': 'Typographie. Papier teinté.',
 'id': {'type': 'Poste', 'yt-no': '1', 'yt-variant': ''},
 'url': 'stamps/Poste-1',
 'image/jpeg': 'T01-000-1.jpg',
 'issued': '1850',
 'perforated-dimensions': 'No',
 'title-en': 'Ceres',
 'title-fr': 'Cérès.',
 'value-en': '10 French centime',
 'value-fr': '10 c.',
 'variants': {'': {'color-en': 'Yellow bistre',
                   'color-fr': 'bistre-jaune',
                   'description-fr': 'Typographie. Papier teinté.',
                   'image/jpeg': 'T01-000-1.jpg',
                   'url': 'stamps/Poste-1',
                   'issued': '1850',
                   'perforated-dimensions': 'No',
                   'title-en': 'Ceres',
                   'title-fr': 'Cérès.',
                   'value-en': '10 French centime',
                   'value-fr': '10 c.',
                   'years': '1849-1850'},
              'a': {'color-en': 'Bistre brown',
                    'color-fr': 'bistre-brun',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-a',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': 'Ceres',
                    'title-fr': 'Cérès.',
                    'value-en': '10 French centime',
                    'value-fr': '10 c.',
                    'years': '1849-1850'},
              'b': {'color-en': '',
                    'color-fr': 'bistre verdâtre',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-b',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 c.',
                    'years': '1849-1850'},
              'c': {'color-en': '',
                    'color-fr': 'bistre verdâtre foncé',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-c',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 c.',
                    'years': '1849-1850'},
              'd': {'color-en': '',
                    'color-fr': 'bistre-jaune Tête-bêche',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-d',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 et 10 c.',
                    'years': '1849-1850'},
              'e': {'color-en': '',
                    'color-fr': 'bistre verdâtre Tête-bêche',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-e',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 et 10 c.',
                    'years': '1849-1850'},
              'f': {'color-en': '',
                    'color-fr': 'bistre clair Réimpression',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-f',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 c.',
                    'years': '1849-1850'}},
 'years': '1849-1850'}


def test_api_stamps_1a(api):
    resource = "/stamps/Poste-1-a"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json() == {'color-en': 'Bistre brown',  'color-fr': 'bistre-brun',
 'description-fr': 'Typographie. Papier teinté.',
 'id': {'type': 'Poste', 'yt-no': '1', 'yt-variant': 'a'},
 'url': 'stamps/Poste-1-a',
 'image/jpeg': 'T01-000-1.jpg',
 'issued': '1850',
 'perforated-dimensions': 'No',
 'title-en': 'Ceres',
 'title-fr': 'Cérès.',
 'value-en': '10 French centime',
 'value-fr': '10 c.',
 'variants': {'': {'color-en': 'Yellow bistre',
                   'color-fr': 'bistre-jaune',
                   'description-fr': 'Typographie. Papier teinté.',
                   'image/jpeg': 'T01-000-1.jpg',
                   'url': 'stamps/Poste-1',
                   'issued': '1850',
                   'perforated-dimensions': 'No',
                   'title-en': 'Ceres',
                   'title-fr': 'Cérès.',
                   'value-en': '10 French centime',
                   'value-fr': '10 c.',
                   'years': '1849-1850'},
              'a': {'color-en': 'Bistre brown',
                    'color-fr': 'bistre-brun',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-a',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': 'Ceres',
                    'title-fr': 'Cérès.',
                    'value-en': '10 French centime',
                    'value-fr': '10 c.',
                    'years': '1849-1850'},
              'b': {'color-en': '',
                    'color-fr': 'bistre verdâtre',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-b',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 c.',
                    'years': '1849-1850'},
              'c': {'color-en': '',
                    'color-fr': 'bistre verdâtre foncé',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-c',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 c.',
                    'years': '1849-1850'},
              'd': {'color-en': '',
                    'color-fr': 'bistre-jaune Tête-bêche',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-d',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 et 10 c.',
                    'years': '1849-1850'},
              'e': {'color-en': '',
                    'color-fr': 'bistre verdâtre Tête-bêche',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-e',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 et 10 c.',
                    'years': '1849-1850'},
              'f': {'color-en': '',
                    'color-fr': 'bistre clair Réimpression',
                    'description-fr': 'Typographie. Papier teinté.',
                    'image/jpeg': 'T01-000-1.jpg',
                    'url': 'stamps/Poste-1-f',
                    'issued': '1850',
                    'perforated-dimensions': 'No',
                    'title-en': '',
                    'title-fr': 'Cérès.',
                    'value-en': '',
                    'value-fr': '10 c.',
                    'years': '1849-1850'}},
 'years': '1849-1850'}

def test_api_stamps_not_found(api):
    resource = "/stamps/0"
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 404
    assert r.json() is None


def test_api_stamp_titles(api):
    resource = "/stamp_titles"
    url = '%s%s' % (API_BASE_URL, resource)
    # First we test that english titles are returned if no explicit Accept-Languages is requested
    r = requests.get(url)
    assert r.status_code == 200
    assert r.headers["Content-Language"] == "en"
    with open("test-data/stamp_titles.json") as f:
        data = json.load(f)
    assert r.json() == data
    # Then we test that english titles are returned if Accept-Languages is set to "en"
    r = requests.get(url, headers={"Accept-Language":"en"})
    assert r.status_code == 200
    assert r.headers["Content-Language"] == "en"
    with open("test-data/stamp_titles.json") as f:
        data = json.load(f)
    assert r.json() == data
    # Then we test that french titles are returned if Accept-Languages is set to "fr"
    r = requests.get(url, headers={"Accept-Language":"fr"})
    assert r.status_code == 200
    assert r.headers["Content-Language"] == "fr"
    with open("test-data/stamp_titles.fr.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_api_stamp_titles_wildcard_search(api):
    resource = ("/stamp_titles"
                "?q=*")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    wildcard_count = 2735
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
    assert r.json()["count"] == 12
    assert [title.endswith("nt") for title in r.json()["stamp_titles"]]


def test_api_stamp_titles_combined_prefix_and_suffix_search(api):
    resource = ("/stamp_titles"
                "?q=C*s")
    url = '%s%s' % (API_BASE_URL, resource)
    r = requests.get(url)
    assert r.status_code == 200
    assert r.json()["count"] == 39
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
