# Faststamps

Faststamps is a [responsive web-application](https://en.wikipedia.org/wiki/Responsive_web_design) for managing a stamp collection. This is a sandbox project for trying out [FastAPI](https://fastapi.tiangolo.com/) & [HTMX](https://htmx.org/) in a tiny micro-service based system, and also for trying out some new technology and ideas.

Since it is a responsive web-application, you can use it in your mobile phone to keep track of your stamp collection.

It consists of:
* A web application **stamp-ui** written in [HTMX](https://htmx.org/) and [Bulma](https://bulma.io/) served by [FastAPI](https://fastapi.tiangolo.com/).
* A backend consisting of two micro-services:
  * A read-only HTTP/JSON API **stamp-catalogue-api** implemented with [FastAPI](https://fastapi.tiangolo.com/) and containing a stamp catalogue, using a CSV file as a database read into a [Pandas](https://pandas.pydata.org/) dataFrame at startup.
  * A HTTP/JSON API **stamp-collection-api** implemented with [FastAPI](https://fastapi.tiangolo.com/) and containing my collection of stamps, using [TinyDB](https://tinydb.readthedocs.io) or [unQLite](https://unqlite.org/) as a database.

The first iteration has a simple authentication mechanism in place in the form of a configuration file containing the single user and that user's salted password hash. Also the first iteration does not make use of FastAPI async support and does not use a multithread-safe database solution.

It is intended to be run as three [Docker](https://www.docker.com) containers with [Docker compose](https://docs.docker.com/compose/). It could be deployed on your laptop, on a home server, or on a virtual server with a VPS provider with Docker and Docker compose. Of course, if you want to access it on your phone from anywhere, you need to deploy it on a server you can access from anywhere.


## Requirements

 * [Python 3.8+](https://www.python.org/) but should probably work with earlier versions too.
 * [FastAPI](https://fastapi.tiangolo.com/).
 * [uvicorn](https://www.uvicorn.org).
 * [HTMX](https://htmx.org/).
 * [Bulma](https://bulma.io/).
 * [Pandas](https://pandas.pydata.org/).
 * [TinyDB](https://tinydb.readthedocs.io).
 * [unQLite](https://unqlite.org/).
 * [Docker](https://www.docker.com) and [Docker compose](https://docs.docker.com/compose/).
 * [Pytest](https://docs.pytest.org).

## Development

Set up the development environment with:

 1. Clone the git repo.
 2. Create a virtual env:
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

### The Faststamps catalogue API

Go to the `stamps-catalogue-api` directory. To start up the stamps-catalogue-api run:
```
$ uvicorn main:app --reload
```

Unit tests are written with Pytest. To run the unit tests:
```
$ pytest -vs
```

### The Faststamps collection API

Go to the `stamps-collection-api` directory. To start up the stamps-collection-api run:

TBD.

### The Faststamps web application

TBD.

# License

This project is released under [GNU GPLv3](LICENSE.TXT).
