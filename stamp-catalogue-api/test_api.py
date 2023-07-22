# This file contains Pytest-based unit tests for the Faststamps Catalogue API
import pytest
from fastapi.testclient import TestClient
from main import app
import os
import json


# Constants
API_PORT = 8008
API_BASE_URL = "http://127.0.0.1:%s" % (API_PORT)
STAMPS_TEST_DATA_FILE = "./test-data/stamps.json"
STAMPS_IMAGE_DIR = "./data/images/large"


@pytest.fixture
def client():
    """We can't just instantiate TestClient like this:
       client = TestClient(app)
       because that will not trigger event handlers in your API app.
       See: https://fastapi.tiangolo.com/advanced/testing-events/"""
    with TestClient(app) as c:
        yield c


def test_root(client):
    resource = "/"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json() == {'name': 'Faststamps Catalogue API.',
                        'version': '0.0.1',
                        'openapi_specification': f'{API_BASE_URL}/docs',
                        'health': f'{API_BASE_URL}/health'}


def test_stamps(client):
    resource = "/stamps"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    with open(STAMPS_TEST_DATA_FILE) as f:
        data = json.load(f)
    assert r.json() == data


def test_stamps_bad_start_and_count(client):
    resource = "/stamps?start=-1"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 400
    assert "Server-timing" in r.headers
    resource = "/stamps?count=-1"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 400
    assert "Server-timing" in r.headers


def test_stamps_filter_title(client):
    resource = ("/stamps"
                "?title=Ceres")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 116


def test_stamps_filter_year(client):
    resource = ("/stamps"
                "?issued=1931,1932,1933")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 54


def test_stamps_filter_color(client):
    resource = ("/stamps"
                "?color=Green,Olive")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 90


def test_stamps_filter_value(client):
    resource = ("/stamps"
                "?value=1 French centime")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 32


def test_stamps_filter_stamp_type(client):
    resource = ("/stamps"
                "?stamp-type=Pour la poste Aérienne")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 127


def test_stamps_combined_filter(client):
    resource = ("/stamps"
                "?title=Ceres"
                "&year=1850,1870,1872"
                "&color=Green,Olive"
                "&value=1 French centime"
                "&stamp_type=timbre")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 3


def test_stamps_count_20(client):
    resource = ("/stamps"
                "?count=20")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 20
    with open("test-data/stamp_count_20.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_stamps_count_20_start_20(client):
    resource = ("/stamps"
                "?start=20"
                "&count=20")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 20
    with open("test-data/stamp_start_20_count_20.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_stamp_poste_1(client):
    resource = "/stamps/Poste-1"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json() == {'color_en': 'Yellow bistre',
                        'color_fr': 'bistre-jaune',
                        'description_fr': 'Typographie. Papier teinté.',
                        'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': ''},
                        'url': 'stamps/Poste-1',
                        'image': 'T01-000-1.jpg',
                        'issued': '1850',
                        'perforated_dimensions': 'No',
                        'title_en': 'Ceres',
                        'title_fr': 'Cérès.',
                        'value_en': '10 French centime',
                        'value_fr': '10 c.',
                        'variants': {'': {'color_en': 'Yellow bistre',
                                          'color_fr': 'bistre-jaune',
                                          'description_fr': 'Typographie. Papier teinté.',
                                          'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': ''},
                                          'image': 'T01-000-1.jpg',
                                          'url': 'stamps/Poste-1',
                                          'issued': '1850',
                                          'perforated_dimensions': 'No',
                                          'title_en': 'Ceres',
                                          'title_fr': 'Cérès.',
                                          'value_en': '10 French centime',
                                          'value_fr': '10 c.',
                                          'years': '1849-1850'},
                                     'a': {'color_en': 'Bistre brown',
                                           'color_fr': 'bistre-brun',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'a'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-a',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': 'Ceres',
                                           'title_fr': 'Cérès.',
                                           'value_en': '10 French centime',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'},
                                     'b': {'color_en': '',
                                           'color_fr': 'bistre verdâtre',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'b'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-b',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'},
                                     'c': {'color_en': '',
                                           'color_fr': 'bistre verdâtre foncé',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'c'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-c',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'},
                                     'd': {'color_en': '',
                                           'color_fr': 'bistre-jaune Tête-bêche',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'd'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-d',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 et 10 c.',
                                           'years': '1849-1850'},
                                     'e': {'color_en': '',
                                           'color_fr': 'bistre verdâtre Tête-bêche',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'e'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-e',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 et 10 c.',
                                           'years': '1849-1850'},
                                     'f': {'color_en': '',
                                           'color_fr': 'bistre clair Réimpression',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'f'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-f',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'}},
                        'years': '1849-1850'}


def test_stamp_poste_1_image(client):
    resource = "/stamps/Poste-1/image"
    # Get image
    f = open(os.path.join(STAMPS_IMAGE_DIR, "T01-000-1.jpg"), "rb")
    image = f.read()
    f.close()
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.content == image


def test_stamp_1a(client):
    resource = "/stamps/Poste-1-a"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json() == {'color_en': 'Bistre brown',
                        'color_fr': 'bistre-brun',
                        'description_fr': 'Typographie. Papier teinté.',
                        'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'a'},
                        'url': 'stamps/Poste-1-a',
                        'image': 'T01-000-1.jpg',
                        'issued': '1850',
                        'perforated_dimensions': 'No',
                        'title_en': 'Ceres',
                        'title_fr': 'Cérès.',
                        'value_en': '10 French centime',
                        'value_fr': '10 c.',
                        'variants': {'': {'color_en': 'Yellow bistre',
                                          'color_fr': 'bistre-jaune',
                                          'description_fr': 'Typographie. Papier teinté.',
                                          'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': ''},
                                          'image': 'T01-000-1.jpg',
                                          'url': 'stamps/Poste-1',
                                          'issued': '1850',
                                          'perforated_dimensions': 'No',
                                          'title_en': 'Ceres',
                                          'title_fr': 'Cérès.',
                                          'value_en': '10 French centime',
                                          'value_fr': '10 c.',
                                          'years': '1849-1850'},
                                     'a': {'color_en': 'Bistre brown',
                                           'color_fr': 'bistre-brun',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'a'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-a',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': 'Ceres',
                                           'title_fr': 'Cérès.',
                                           'value_en': '10 French centime',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'},
                                     'b': {'color_en': '',
                                           'color_fr': 'bistre verdâtre',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'b'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-b',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'},
                                     'c': {'color_en': '',
                                           'color_fr': 'bistre verdâtre foncé',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'c'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-c',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'},
                                     'd': {'color_en': '',
                                           'color_fr': 'bistre-jaune Tête-bêche',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'd'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-d',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 et 10 c.',
                                           'years': '1849-1850'},
                                     'e': {'color_en': '',
                                           'color_fr': 'bistre verdâtre Tête-bêche',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'e'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-e',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 et 10 c.',
                                           'years': '1849-1850'},
                                     'f': {'color_en': '',
                                           'color_fr': 'bistre clair Réimpression',
                                           'description_fr': 'Typographie. Papier teinté.',
                                           'id': {'type': 'Poste', 'yt_no': '1', 'yt_variant': 'f'},
                                           'image': 'T01-000-1.jpg',
                                           'url': 'stamps/Poste-1-f',
                                           'issued': '1850',
                                           'perforated_dimensions': 'No',
                                           'title_en': '',
                                           'title_fr': 'Cérès.',
                                           'value_en': '',
                                           'value_fr': '10 c.',
                                           'years': '1849-1850'}},
                        'years': '1849-1850'}


def test_stamp_not_found(client):
    resource = "/stamps/0"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 404
    assert "Server-timing" in r.headers
    assert r.json() is None


def test_stamp_titles(client):
    resource = "/stamp_titles"
    url = '%s%s' % (API_BASE_URL, resource)
    # First we test that english titles are returned if no explicit Accept-Languages is requested
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.headers["Content-Language"] == "en"
    with open("test-data/stamp_titles.json") as f:
        data = json.load(f)
    assert r.json() == data
    # Then we test that english titles are returned if Accept-Languages is set to "en"
    r = client.get(url, headers={"Accept-Language": "en"})
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.headers["Content-Language"] == "en"
    with open("test-data/stamp_titles.json") as f:
        data = json.load(f)
    assert r.json() == data
    # Then we test that french titles are returned if Accept-Languages is set to "fr"
    r = client.get(url, headers={"Accept-Language": "fr"})
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.headers["Content-Language"] == "fr"
    with open("test-data/stamp_titles.fr.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_stamp_titles_wildcard_search(client):
    resource = ("/stamp_titles"
                "?q=*")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    wildcard_count = 2735
    assert r.json()["count"] == wildcard_count
    url = '%s%s' % (API_BASE_URL, "/stamp_titles")
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == wildcard_count


def test_stamp_titles_prefix_search(client):
    resource = ("/stamp_titles"
                "?q=Ce*")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 53
    assert [title.startswith("Ce") for title in r.json()["values"]]


def test_stamp_titles_suffix_search(client):
    resource = ("/stamp_titles"
                "?q=*nt")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 12
    assert [title.endswith("nt") for title in r.json()["values"]]


def test_stamp_titles_combined_prefix_and_suffix_search(client):
    resource = ("/stamp_titles"
                "?q=C*s")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    assert r.json()["count"] == 39
    assert [title.startswith("C") and title.endswith("s") for title in r.json()["values"]]


def test_stamp_titles_wildcard_search_multiple_stars(client):
    resource = ("/stamp_titles"
                "?q=**")
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 400
    assert "Server-timing" in r.headers
    assert r.json() == "Multiple wildcard stars '*' in query is not supported."


def test_stamp_years(client):
    resource = "/stamp_years"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    with open("test-data/stamp_years.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_stamp_colors(client):
    resource = "/stamp_colors"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    with open("test-data/stamp_colors.json") as f:
        data = json.load(f)
    assert r.json() == data


def test_stamp_values(client):
    resource = "/stamp_values"
    url = '%s%s' % (API_BASE_URL, resource)
    r = client.get(url)
    assert r.status_code == 200
    assert "Server-timing" in r.headers
    with open("test-data/stamp_values.json") as f:
        data = json.load(f)
    assert r.json() == data
