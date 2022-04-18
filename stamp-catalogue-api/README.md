# Faststamps Catalogue API

The Faststamps Catalogue API is a read-only HTTP/JSON API implemented with FastAPI and containing a stamp catalogue. It uses a CSV file as a database read into a Pandas dataFrame at startup. It is meant to be run as a backend micro-service API providing the Faststamps app with a stamp catalogue with info on stamps.

It has its own requirements.txt file, it's own unit tests and its own Dockerfile. It is meant to be deployed together with the Faststamps Collection API and Faststamps app as a Docker service with three Docker containers.

## Requirements

 * [Python 3.8+](https://www.python.org/) but should probably work with earlier versions too.
 * [FastAPI](https://fastapi.tiangolo.com/).
 * [uvicorn](https://www.uvicorn.org).
 * [Pandas](https://pandas.pydata.org/).
 * [Docker](https://www.docker.com).
 * [Pytest](https://docs.pytest.org).

It also needs a stamp catalogue in CSV-format. There is a `french-stamps.csv` in this directory, with all French stamps from 1849-1999. I have created that file from various sources on the net. If you want to include stamp images you will need to create a directory `images` and then add stamp images where each image file has the name `<id>.jpg`, where <id> is the id used in the first column of the CSV file. In the `french-stamps.csv` file the first column contains the Yvert-Tellier number of the stamp. You can use another id if you want to, as long as the id used in the CSV file is consistent with the id used in the stamp image file names.

## Development

Set up the development environment for Faststamps Catalogue API with:

 1. Clone the git repo for Faststamps.
 2. In this subdirectory `stamp-catalogue-api`, create a virtual env:
```
$ virtualenv -p python3 env
```
 3. Jump into the virtual env:
```
$ source env/bin/activate
```
 4. Install dependent packages with:
```
$ pip install -r requirements.txt
```

To run flake8 linting:
```
$ flake8 --config flake8.conf
```

To run the stamps-catalogue-api:
```
$ uvicorn main:app --reload
```

You can then access the API locally at: http://127.0.0.1:8000.

Unit tests are written with Pytest. The unit test program `test_api.py` runs the API on a different port than the default port, so you can have the API running as described above, and run the init tests at the same time. To run the unit tests:
```
$ pytest -vs
```
