from fastapi import FastAPI, Request, Response, status  # Path, Query, Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
# from typing import Optional, List
# from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings
import os.path
import datetime
import time
import hashlib


class Settings(BaseSettings):
    """Provides configuration and environment variables via the Pydantic BaseSettings class. Values
       are read in this order:
       1) Environment variables. If they are not set then from
       2) Key/values from a ".env" file. If they are not set there then from
       3) Default values set in this class."""
    VERSION: str = "0.0.1"
    TEMPLATES_DIR: str = "templates"
    DATE_FORMAT: str = "Date: %a, %d %b %Y %H:%M:%S"

    class ConfigDict:
        env_file = ".env"


settings = Settings()
templates = Jinja2Templates(directory=settings.TEMPLATES_DIR)


# Utility functions
def md5_digest(file_name):
    """The md5 digest of the file `file_name`."""
    hash_md5 = hashlib.md5()
    with open(file_name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return f"\"{hash_md5.hexdigest()}\""


app = FastAPI(
    title="The Faststamps web app",
    version=settings.VERSION)


@app.get("/")
async def get_index_file(request: Request) -> HTMLResponse:
    """The main application page (index.html)."""
    tic = time.perf_counter_ns()
    result = templates.TemplateResponse("index.html", {"request": request})
    print("/")
    # Set Last-modified and Etag headers
    path = os.path.join(settings.TEMPLATES_DIR, "index.html")
    m_time = os.path.getmtime(path)
    m_time_str = datetime.datetime.fromtimestamp(m_time).strftime(settings.DATE_FORMAT)
    result.headers["Last-modified"] = m_time_str
    result.headers["Etag"] = md5_digest(path)
    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in milliseconds, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/{file}")
async def get_file(file: str, response: Response) -> FileResponse:
    """Return the file with the given name."""
    tic = time.perf_counter_ns()
    path = os.path.join(file)
    print("/{file}")
    if os.path.exists(path):
        result = FileResponse(path, media_type="")
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in milliseconds, not including FastAPI itself)
        result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return result
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in milliseconds, not including FastAPI itself)
        response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
        return None
