from fastapi import FastAPI, Request, Response, Query, Path, status  # Header
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, Annotated  # List
# from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings
import os.path
import httpx
import datetime
import time
import hashlib
import search_navigation


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
    RESULTS_PER_PAGE: int = 20

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


@app.get("/")
async def get_index_file(request: Request) -> HTMLResponse:
    """The main application page (index.html)."""
    tic = time.perf_counter_ns()
    result = templates.TemplateResponse("index.html", {"request": request})
    path = os.path.join(settings.TEMPLATES_DIR, "index.html")
    m_time = os.path.getmtime(path)
    m_time_str = datetime.datetime.fromtimestamp(m_time).strftime(settings.DATE_FORMAT)
    # Set Last-modified and Etag headers
    result.headers["Last-modified"] = m_time_str
    result.headers["Etag"] = md5_digest(path)
    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/search")
async def get_search(request: Request,
                     q: Optional[str] = Query(None,
                                              description="Search query"),
                     start: Optional[int] = Query(None,
                                                  description="Start result")) -> HTMLResponse:
    """The search page (search.hmtl)."""
    tic = time.perf_counter_ns()
    if q:
        url = f"{settings.CATALOGUE_API_URL}stamps?title={q}"
        print(f"!!url: {url}")
        r = httpx.get(url)
        if r.status_code == 200:
            results = r.json()
            seconds = float(r.headers["server-timing"].split("=")[1])/1000
            if not start:
                start = 0
            rps = search_navigation.result_pages_specification(results["count"],
                                                               start,
                                                               settings.RESULTS_PER_PAGE,
                                                               linked_pages=10,
                                                               first_page=True,
                                                               last_page=True)
            stamps = results["stamps"][start:start+settings.RESULTS_PER_PAGE]
            result = templates.TemplateResponse("search.html",
                                                {"request": request,
                                                 "count": results["count"],
                                                 "rps": rps,
                                                 "stamps": stamps,
                                                 "seconds": f"{seconds:.3}"})
            result.headers["HX-Push"] = f"/search?q={q}"
    else:
        rps = None
        result = templates.TemplateResponse("search.html", {"request": request})
    toc = time.perf_counter_ns()
    # Set Server-timing header (server excution time in ms, not including FastAPI itself)
    result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/search_results")
async def get_search_results(request: Request, response: Response,
                             q: Optional[str] = Query(None,
                                                      description="Search query"),
                             start: Optional[int] = Query(None,
                                                          description="Start")) -> HTMLResponse:
    """HTML representation of the search results (search_results.html)."""
    tic = time.perf_counter_ns()
    # Get search results from Catalogue API
    if q:
        url = f"{settings.CATALOGUE_API_URL}stamps?title={q}"
    else:
        url = f"{settings.CATALOGUE_API_URL}stamps"
    print(f"url: {url}")
    r = httpx.get(url)
    # Set up the HTMX-response
    if r.status_code == 200:
        results = r.json()
        # Generate HTML search result with appropriate Jinja2template
        seconds = float(r.headers["server-timing"].split("=")[1])/1000
        if not start:
            start = 0
        rps = search_navigation.result_pages_specification(results["count"],
                                                           start,
                                                           settings.RESULTS_PER_PAGE,
                                                           linked_pages=10,
                                                           first_page=True,
                                                           last_page=True)
        stamps = results["stamps"][start:start+settings.RESULTS_PER_PAGE]
        if q == "Empereur Napoleon III":
            print(stamps)
        result = templates.TemplateResponse("search_results.html",
                                            {"request": request,
                                             "count": results["count"],
                                             "rps": rps,
                                             "stamps": stamps,
                                             "seconds": f"{seconds:.3}"})
        result.headers["HX-Push"] = f"/search?q={q}"
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        result.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        if q == "Empereur Napoleon III":
            print(result.body)
        return result
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return response


@app.get("/stamp_variants/{stamp_id}")
async def get_stamp_variants(request: Request, response: Response,
                             stamp_id: Annotated[str, Path(title="Id of stamp")]) -> HTMLResponse:
    """HTML representation of a stamps variants."""
    tic = time.perf_counter_ns()
    url = f"{settings.CATALOGUE_API_URL}stamps/{stamp_id}"
    print(f"url: {url}")
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


@app.get("/stamp_image/{stamp_id}")
async def get_stamp_image(response: Response,
                          stamp_id: Annotated[str, Path(title="Id of stamp")]) -> Response:
    tic = time.perf_counter_ns()
    url = f"{settings.CATALOGUE_API_URL}stamps/{stamp_id}/image"
    print(f"url: {url}")
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


@app.get("/{file}")
async def get_file(file: str, response: Response) -> FileResponse:
    """Return the file (binary contents) with the given name."""
    tic = time.perf_counter_ns()
    path = os.path.join(file)
    if os.path.exists(path):
        result = FileResponse(path)
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return result
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Set Server-timing header (server excution time in ms, not including FastAPI itself)
        response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
        return None
