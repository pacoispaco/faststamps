# Faststamps App

The Faststamps App is a web app implemented with HTMX, Bulma CSS and FastAPI & Uvicorn. It consists
of two parts:

 * **web-app**: A web application frontend implemented in HTMX, Bulma CSS and a minimum amount of
   Javascript and a few image assets. This is served by Nginx and packaged as a Docker image.
 * **web-app-api**: A web application BFF (Backend For Frontend) API implemented in Python and
   FastAPI that serves responses to HTMX-generated HTTP requests from the web application frontend.
   This is served by Uvicorn and is also packaged as a Docker image.

## Requirements

For the web-app-api:

 * [Python 3.10](https://www.python.org/), but should probably work with Python 3.8+.
 * [FastAPI](https://fastapi.tiangolo.com/).
 * [uvicorn](https://www.uvicorn.org).
 * [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/)?
 * [Pytest](https://docs.pytest.org).

For the web-app:

 * [HTMX](https://htmx.org/).
 * [Bulma CSS](://bulma.io/).

For packaging, deploying and running:

 * [Docker](https://www.docker.com).

For the web-app and web-app-api to fully work they need running instances of the Faststamps
Catalogue API and the Faststamps Collection API.

## Getting started

Clone repo and set up development environment:

```bash
$ git clone git@github.com:pacoispaco/faststamps.git
```

### web-app-api

Go to the `stamps-app/web-app-api` directory and run:

```bash
cd stamps-app/web-app-api
virtualenv -p python3 env
source env/bin/activate
pip install -r requirements.txt
```

To run flake8 linting:

```bash
flake8 --config flake8.conf
```

To run tests:

```bash
pytest -vs
```

Currently there are no unit tests for the web-app-api. But they will be written with Pytest. To run the unit tests:

```bash
pytest -vs
```

To build the Docker image that serves the API with Uvicorn:

```bash
docker build -t web-app-api .
```

To run the Docker image and access it at port 8081:

```bash
docker run -d -p 8080:81 web-app-api
```

You can then access the API locally at: http://127.0.0.1:8081.

If you want to run the web-app-api directly as a uvicorn server:

```bash
uvicorn main:app --reload --port 8081
```

You can then access the API locally at: http://127.0.0.1:8080. But of course you can't run that if
you have a web-app-api Docker container already running on the same port.


### web-app

Go to the `stamps-app/webb-app` directory.

To build the Docker image that serves the web-app with Nginx:

```bash
docker build -t web-app .
```

To run the Docker image and access it at port 8080:

```bash
docker run -d -p 8080:80 web-app
```

You can then access the web-app locally at: http://127.0.0.1:8080.
