from fastapi import FastAPI, Request, Response, Query, Path, status  # Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Annotated  # List
# from pydantic import BaseSettings
from pydantic_settings import BaseSettings
import os.path
import logging
import logging.config
import httpx
import time
import hashlib
import search


class Settings(BaseSettings):
    """Provides configuration and environment variables via the Pydantic BaseSettings class. Values
       are read in this order:
       1) Environment variables. If they are not set then from
       2) Key/values from a ".env" file. If they are not set there then from
       3) Default values set in this class."""
    VERSION: str = "0.0.1"
    TEMPLATES_DIR: str = "templates"
    DATE_FORMAT: str = "Date: %a, %d %b %Y %H:%M:%S"
    CATALOGUE_API_URL: str = "http://127.0.0.1:8081/"
    RESULTS_PER_PAGE: int = 5
    LOGGING_LEVEL: str = "DEBUG"
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(LOGGING_LEVEL)

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


def non_variant_stamps(stamps):
    """Return a list of the subset of `stamps` that are not variant stamps."""
    return [stamp for stamp in stamps if stamp["id"]["yt_variant"] == '']


app = FastAPI(
    title="The Faststamps web app",
    version=settings.VERSION)


@app.get("/", response_class=HTMLResponse)
async def get_index_file(request: Request,
                         start: int = Query(default=0,
                                            description="Start result")):
    """The main application page (index.html)."""
    tic = time.perf_counter_ns()

    # Get all stamps from the API
    url = f"{settings.CATALOGUE_API_URL}stamps"
    settings.logger.debug(f"(get_index_file) url: {url}")
    r = httpx.get(url)
    settings.logger.debug(f"(get_index_file) r.status_code: {r.status_code}")
    if r.status_code == 200:
        ssr = search.stamp_search_results("",
                                          r,
                                          start,
                                          settings.RESULTS_PER_PAGE)
        rps = search.search_result_page_spec(ssr.stamps_count,
                                             start,
                                             settings.RESULTS_PER_PAGE,
                                             linked_pages=10,
                                             first_page=True,
                                             last_page=True)
        result = templates.TemplateResponse("index.html",
                                            {"request": request,
                                             "ssr": ssr,
                                             "rps": rps})
    else:
        rps = None
        result = templates.TemplateResponse("index.html", {"request": request})

    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/search", response_class=HTMLResponse)
async def get_search(request: Request, response: Response,
                     q: Optional[str] = Query(None,
                                              description="Search query"),
                     start: int = Query(default=0,
                                        description="Start result")):
    """The search page (search.hmtl)."""
    tic = time.perf_counter_ns()
    if q:
        url = f"{settings.CATALOGUE_API_URL}stamps?title={q}"
        r = httpx.get(url)
        if r.status_code == 200:
            ssr = search.stamp_search_results(q,
                                              r,
                                              start,
                                              settings.RESULTS_PER_PAGE)
            rps = search.search_result_page_spec(ssr.stamps_count,
                                                 start,
                                                 settings.RESULTS_PER_PAGE,
                                                 linked_pages=10,
                                                 first_page=True,
                                                 last_page=True)
            result = templates.TemplateResponse("index.html",
                                                {"request": request,
                                                 "ssr": ssr,
                                                 "rps": rps})
            result.headers["HX-Push"] = f"/search?q={q}"
        else:
            result = response
    else:
        rps = None
        result = templates.TemplateResponse("index.html", {"request": request})
    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/search_results", response_class=HTMLResponse)
async def get_search_results(request: Request, response: Response,
                             q: Optional[str] = Query(None,
                                                      description="Search query"),
                             start: int = Query(default=0,
                                                description="Start")):
    """HTML representation of the search results (search_results.html)."""
    tic = time.perf_counter_ns()
    settings.logger.debug(f"get_search_results: q='{q}'")
    # Make sure to strip query string of leading and trailing white space.
    q = q.strip()
    # Get search results from Catalogue API
    if q:
        url = f"{settings.CATALOGUE_API_URL}stamps?title={q}"
    else:
        url = f"{settings.CATALOGUE_API_URL}stamps"
    r = httpx.get(url)
    # Set up the HTMX-response
    if r.status_code == 200:
        ssr = search.stamp_search_results(q,
                                          r,
                                          start,
                                          settings.RESULTS_PER_PAGE)
        rps = search.search_result_page_spec(ssr.stamps_count,
                                             start,
                                             settings.RESULTS_PER_PAGE,
                                             linked_pages=10,
                                             first_page=True,
                                             last_page=True)
        result = templates.TemplateResponse("search_results.html",
                                            {"request": request,
                                             "ssr": ssr,
                                             "rps": rps})
        # Set the URL for the returned page and make sure the browser is updated
        if q:
            path = f"/search?q={q}"
            if start > 0:
                path += f"&start={start}"
        else:
            path = "/"
            if start > 0:
                path += f"?start={start}"
        result.headers["HX-Push"] = path
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return result
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return response


@app.get("/stamp_variants/{stamp_id}", response_class=HTMLResponse)
async def get_stamp_variants(request: Request, response: Response,
                             stamp_id: Annotated[str, Path(title="Id of stamp")]):
    """HTML representation of a stamps variants."""
    tic = time.perf_counter_ns()
    url = f"{settings.CATALOGUE_API_URL}stamps/{stamp_id}"
    r = httpx.get(url)
    if r.status_code == 200:
        variants = r.json()["variants"]
        # Generated HTML variants result with appropriate Jinja2template
        result = templates.TemplateResponse("stamp_variants.html",
                                            {"request": request,
                                             "variants": variants})
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return result
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"


@app.get("/stamp_image/{stamp_id}", response_class=Response)
async def get_stamp_image(response: Response,
                          stamp_id: Annotated[str, Path(title="Id of stamp")]):
    tic = time.perf_counter_ns()
    url = f"{settings.CATALOGUE_API_URL}stamps/{stamp_id}/image"
    r = httpx.get(url)
    if r.status_code == 200:
        image = r.content
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return Response(content=image, media_type="image/jpeg")
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return response


@app.get("/{file}", response_class=FileResponse)
async def get_file(file: str, response: Response):
    """Return the file (binary contents) with the given name."""
    tic = time.perf_counter_ns()
    path = os.path.join(file)
    if os.path.exists(path):
        result = FileResponse(path)
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return result
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return response
