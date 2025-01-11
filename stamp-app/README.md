# Faststamps App

The Faststamps App is a web app implemented with HTMX, Bulma CSS and FastAPI & Uvicorn.

## Requirements

For development:

 * [Python 3.10](https://www.python.org/), but should probably work with Python 3.8+.
 * [FastAPI](https://fastapi.tiangolo.com/).
 * [uvicorn](https://www.uvicorn.org).
 * [Jinja2](https://jinja.palletsprojects.com/en/3.1.x/).
 * [httpx](https://www.python-httpx.org/).
 * [Pytest](https://docs.pytest.org).
 * [HTMX](https://htmx.org/).
 * [Bulma CSS](://bulma.io/).

For packaging, deploying and running:

 * [Docker](https://www.docker.com).

For the app to fully work it needs running instances of the Faststamps catalog API and the Faststamps Collection API.

## Getting started

Clone repo and set up development environment:

```bash
$ git clone git@github.com:pacoispaco/faststamps.git
```

Go to the `stamp-app` directory and run:

```bash
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

To build the Docker image that serves the API with Uvicorn:

```bash
docker build -t stamps-app .
```

To run the Docker image and access it at port 8081:

```bash
docker run -d -p 8080:80 stamps-app
```

You can then access the app locally at: http://127.0.0.1:8080.

If you want to run the app directly as a uvicorn server:

```bash
uvicorn main:app --reload --port 8080
```

You can then access the app locally at: http://127.0.0.1:8080. But of course you can't run that if
you have a app Docker container already running on the same port.
