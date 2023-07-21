from fastapi import FastAPI, Request, Response  # , status, Path, Query, Header
# from fastapi.responses import FileResponse
# from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings
# import os.path
import time

description = """
## Faststamps web app BFF (Backend For Frontend) API

This API provides HTMX-resources for the Faststamps web app.
"""


class Settings(BaseSettings):
    """Provides configuration and environment variables via the Pydantic BaseSettings class. Values
       are read in this order:
       1) Environment variables. If they are not set then from
       2) Key/values from a ".env" file. If they are not set there then from
       3) Default values set in this class."""
    VERSION: str = "0.0.1"

    class ConfigDict:
        env_file = ".env"


settings = Settings()


# Pydantic data classes used in the API
class ApiInfo(BaseModel):
    """Represents information on the API."""
    name: str           # Name of the API
    version: str        # Version of the API (implementation version, not interface version)
    openapi_specification: HttpUrl  # URL to API docs
    health: HttpUrl     # URL to resource with info on the health of the API


# Utility functions


app = FastAPI(
    title="The Faststamps web app BFF (Backend For Frontend) API",
    description=description,
    version=settings.VERSION)


@app.on_event("startup")
def startup_event():
    """Initialize the API."""


@app.on_event("shutdown")
async def shutdown():
    pass


@app.get("/", tags=["HTMX resource API"])
def api_root_resource(request: Request, response: Response) -> ApiInfo:
    """The root resource. Returns the name of this API, its version, and an URL where the OpenAPI
       specification of this API can be found. The version number identifies the implementation
       version and not the interface version."""
    tic = time.perf_counter_ns()
    result = {"name": "Faststamps Catalogue API.",
              "version": settings.VERSION,
              "openapi_specification": str(request.url) + "docs",
              "health": str(request.url) + "health"}
    toc = time.perf_counter_ns()
    # Return total server xecution time in milliseconds (not including FastAPI itself)
    response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result
