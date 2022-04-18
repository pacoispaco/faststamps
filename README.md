![Flake8 linting](https://github.com/pacoispaco/faststamps/actions/workflows/flake8.yml/badge.svg) ![Pytest unit tests](https://github.com/pacoispaco/faststamps/actions/workflows/pytest.yml/badge.svg)

# Faststamps app

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

The total requirements are as follows, but note that the Faststamps app, Catalogue API and Collection API have slightly different dependencies and all have their own `requirements.txt`files.

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

Set up the development environment by first cloning the git repo.

There are three separate directories for the thre components of Faststamps; Faststamps app, Catalogue API and Collection API. You should set up separate virtual environments in each directory and work locally with each component in the respective directory, as described in the respective README.md files:

 * [stamp-catalogue-api/README.md](stamp-catalogue-api/README.md).
 * [stamp-collection-api/README.md](stamp-collection-api/README.md).
 * [stamp-app/README.md](stamp-app/README-md).

This top level directory contains a Docker compose file for locally starting up all containers as a service.

# License

This project is released under [GNU GPLv3](LICENSE.TXT).
