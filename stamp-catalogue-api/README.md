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

## The stamp catalog CSV file

The Catalogue API will read a stamp catalogue in CSV format. The API assumes the following structure of CSV file:

* The first row contains column headers and the subsequent rows contain data on individal stamps.
* Each row must represent data on a single stamp.
* The first column must contain a unique id for the stamp.
* The column headers are interpreted as follows:
  * The first column must have a column name beginning with **id-\<scheme\>**, followed by some name identifying the id scheme. E.g **id-yt** would denote that the Yvert-Tellier catalogue numbering scheme is being used to identify the stamps.
  * After the first column, the following column names are recommended but none is required:
    - **id-\<id-scheme\>**. You can have more columns with stamp ids, based on other id schemes. E.g. **id-mi** for Michel catalogue numbers.
    - **type-\<lang\>**. The type of the stamp, where <lang> is the same as above. E.g. the column name **type-fr**.
    - **issued**. The year the stamp was first issued. E.g. the value **1849**.
    - **years**. The years during which stamps in this series were issued. Note that the catalogue numbers do not necessarily reflect the order in which stamps were issued. E.g. the value **1849-1850**.
    - **title-\<lang\>**. The descriptive title of the stamp, where <lang> is a ISO 639-1 language code, specifying the language. There can be multiple title columns, each with a different language code. E.g. the column names **title-en** and **title-fr**.
    - **value-\<lang\>**. The printed value of the stamp, where <lang> is the same as above. E.g. the column names **value-en** and **value-fr**.
    - **color-\<lang\>**. The color of the stamp, where <lang> is the same as above. E.g. the column names **color-en** and **color-fr**.
    - **description-\<lang\>**. The description of the kind of stamp, where <lang> is the same as above. E.g. the column names **description-en** and **description-fr**.
    - **perforated**. Is the stamp perforated or not. Values can be **no** or **yes**.
    - **\<media-type\>**. Link to media file for the stamp, where <media-type> is a [IANA media type](https://www.iana.org/assignments/media-types/media-types.xhtml). E.g. the column name **image/jpeg**.
