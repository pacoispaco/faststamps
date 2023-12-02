from fastapi import FastAPI, status, Request, Response, Path, Query, Header
from fastapi.responses import FileResponse
from typing import Optional, List
from pydantic import BaseModel, HttpUrl
from pydantic_settings import BaseSettings
import pandas as pd
import numpy as np
import os.path
import time

description = """
## Faststamps Catalog API

This is a simple API for retrieving information on stamps in a stamp catalog. This is a read-only
API.
"""


class Settings(BaseSettings):
    """Provides configuration and environment variables via the Pydantic BaseSettings class. Values
       are read in this order:
       1) Environment variables. If they are not set then from
       2) Key/values from a ".env" file. If they are not set there then from
       3) Default values set in this class."""
    VERSION: str = "0.0.1"
    STAMP_CATALOG_CSV_FILE: str = "./data/french-stamps.csv"
    STAMP_CATALOG_IMAGES_DIR: str = "./data/images/large"

    class ConfigDict:
        env_file = ".env"


settings = Settings()


# Globals. :-# OMG! What did I do!?
# These "databases" are simply Pandas Dataframes. One holds the stamps CSV file and the other simply
# is an indexed version of the former.
db = None
indexed_db = None


# Pydantic data classes used in the API
class ApiInfo(BaseModel):
    """Represents information on the API."""
    name: str           # Name of the API
    version: str        # Version of the API (implementation version, not interface version)
    openapi_specification: HttpUrl  # URL to API docs
    health: HttpUrl     # URL to resource with info on the health of the API


class StampId(BaseModel):
    """The attributes that uniquely identify a stamp."""
    type: str         # Eg. "Poste"
    yt_no: str        # Eg. "1"
    yt_variant: str   # Eg. "a"


class Stamp(BaseModel):
    """Represents a stamp (possibly a variant)."""
    color_en: str               # Eg. 'Yellow bistre'
    color_fr: str               # Eg. 'bistre-jaune'
    description_fr: str         # Eg. 'Typographie. Papier teinté.'
    id: StampId                 # Eg. 'type': 'Poste', 'yt-no': '1', 'yt-variant': ''}
    url: str                    # Eg. 'stamps/Poste-1'
    image: str                  # Eg. 'T01-000-1.jpg'
    issued: str                 # Eg. '1850'
    perforated_dimensions: str  # Eg. 'No'
    title_en: str               # Eg. 'Ceres'
    title_fr: str               # Eg. 'Cérès.'
    value_en: str               # Eg. '10 French centime'
    value_fr: str               # Eg. '10 c.'
    years: str                  # Eg. '1849-1850'


class StampWithVariants(Stamp):
    """Represents a stamp with information on its variants."""
    variants: dict[str, Stamp]


class StampList(BaseModel):
    """Represents a list of stamps."""
    count: int
    stamps: List[Stamp]


class StringValuesList(BaseModel):
    """Represents a list of string values."""
    count: int
    values: List[str]


# Utility functions
def convert_db_stamp_to_api_stamp(d: dict):
    """Convert the stamp dict `d` from the stamp DB to an API stamp dict that can be parsed to a
       Stamp model object."""
    id = {"yt_no": d["id_yt_no"],
          "yt_variant": d["id_yt_var"],
          "type": d["type_fr"]}
    d["id"] = id
    del d["id_yt_no"]
    del d["id_yt_var"]
    del d["type_fr"]


def parsed_accept_language(accept_language):
    """Parse the `accept_language` string and return a list of tuples containing the languages and
       their factor weighting (q), ordered from highest-to-lowest factor weighting."""
    if accept_language is None:
        return ('en', '1')
    else:
        languages = accept_language.split(",")
        result = []
        for language in languages:
            if language.split(";")[0] == language:
                # If no explicit factor weighting, we assume it is 1 (q => q = 1)
                result.append((language.strip(), "1"))
            else:
                locale = language.split(";")[0].strip()
                q = language.split(";")[1].split("=")[1]
                result.append((locale, q))
        return result


app = FastAPI(
    title="The Faststamps Catalog API",
    description=description,
    version=settings.VERSION)


@app.on_event("startup")
def startup_event():
    """Initialize the API by initializing the database. That means opening the local CSV-file
       containing a full stamp catalog and then reading into some suitable in-memory data
       structure."""
    global db, indexed_db
    if os.path.exists(settings.STAMP_CATALOG_CSV_FILE):
        with open(settings.STAMP_CATALOG_CSV_FILE) as f:
            db = pd.read_csv(f, delimiter=';', dtype={'issued': str, 'id_yt_no': str})
            # We replace all np.NAN with an empty string "" and create a multindex
            # consisting of the stamp type, Yt no and variant.
            db = db.replace({np.NaN: ""})
            # Add URL column
            db["url"] = db[["type_fr", "id_yt_no", "id_yt_var"]].apply(
                    lambda x: f"stamps/{x[0]}-{x[1]}-{x[2]}" if x[2]
                              else f"stamps/{x[0]}-{x[1]}", axis=1)
            # Create index of db and sort the index
            indexed_db = db.set_index(["type_fr", "id_yt_no", "id_yt_var"])
            indexed_db = indexed_db.sort_index()


@app.on_event("shutdown")
async def shutdown():
    pass


@app.get("/", tags=["stamps"])
def api_root_resource(request: Request, response: Response) -> ApiInfo:
    """The root resource. Returns the name of this API, its version, and an URL where the OpenAPI
       specification of this API can be found. The version number identifies the implementation
       version and not the interface version."""
    tic = time.perf_counter_ns()
    result = {"name": "Faststamps Catalog API.",
              "version": settings.VERSION,
              "openapi_specification": str(request.url) + "docs",
              "health": str(request.url) + "health"}
    toc = time.perf_counter_ns()
    # Return total server xecution time in milliseconds (not including FastAPI itself)
    response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/stamps", tags=["stamps"])
def get_stamps(response: Response,
               title: Optional[str] = Query(None,
                                            description="""Return stamps that have the given
                                            `title`."""),
               issued: Optional[str] = Query(None,
                                             description="""Return stamps that were 'issued' in
                                                            that year. `issued` can be a comma-
                                                            separated list of years."""),
               color: Optional[str] = Query(None,
                                            description="""Return stamps with the given `color`.
                                                           `color` can be a comma-separated list
                                                           of colors."""),
               value: Optional[str] = Query(None,
                                            description="""Return stamps with the given printed
                                                           `value`. `value` can be a comma-
                                                           separated list of values."""),
               stamp_type: Optional[str] = Query(None,
                                                 description="""Return stamps of the given
                                                                `stamp_type`. `stamp_type` can
                                                                be a comma-separated list of
                                                                values.""",
                                                 alias="stamp-type"),
               start: Optional[int] = Query(None,
                                            description="""Return the stamps beginning with stamp
                                                           at `start` position in the list of
                                                           stamps. If not given, `start` is
                                                           implicitly 1. Must be >= 1."""),
               count: Optional[int] = Query(None,
                                            description="""Return the given `count` of stamps from
                                                           the list of stamps. If not given,
                                                           `count` is implicitly 'all'. Must
                                                           be >= 1."""),
               accept_language: Optional[str] = Header(None)) \
               -> StampList | None:
    """Return the catalog of stamps. If no query parameter is specified all stamps in the
       catalog are returned. All query parameters can be combined.

NOTE: THIS VERSION IS DONE WITH PYDANTIC CLASSES.

The query parameters `title`, `year`, `color`, `value` and `stamp_type` can be used to filter
which stamps to return from the catalog.

The query parameters `start`and `count` control which and how many number of the, possibly
filtered, stamps in the catalog to return.

Examples:

* `/stamps` will return all stamps.
* `/stamps?title=Marianne` will return all stamps with the name "Marianne". Use the HTTP header
* Accept-language to denote the language of the title. 'en' (English) and 'fr' (French) are
* supported If none is specified, or if the language is none of the supported, English is assumed.
* `/stamps?issued=1931,1932,1933` will return all stamps issued in 1931, 1932 or 1933.
* `/stamps?color=Green,Olive` will return all stamps that are colored "Green" or "Olive".
* `/stamps?value=1 French centime` will return all stamps with the printed value of "1 French
centime".
* `/stamps?stamp_type=timbre` will return all stamps of typ "timbre".
* `/stamps?start=1000` will return all stamps beginning with the 1000:th stamp.
* `/stamps?count=100` will return a maximum of 100 stamps.
    """
    tic = time.perf_counter_ns()
    language = parsed_accept_language(accept_language)[0][0]
    if start is not None and start <= 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.body = "Query parameter 'start' must be >= 1."
        toc = time.perf_counter_ns()
        # Return total server xecution time in milliseconds (not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return None
    if count is not None and count <= 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.body = "Query parameter 'count' must be >= 1."
        toc = time.perf_counter_ns()
        # Return total server xecution time in milliseconds (not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return None
    # We apply successive filters on the pandas dataFrame `db`
    stamps = db
    if title is not None:
        if language[0:2] == "fr":
            stamps = stamps[stamps["title_fr"] == title]
        else:
            stamps = stamps[stamps["title_en"] == title]
    if issued is not None:
        issued_years = [item for item in issued.split(',')]
        stamps = stamps[stamps["issued"].isin(issued_years)]
    if color is not None:
        colors = color.split(',')
        if language[0:2] == "fr":
            stamps = stamps[stamps["color_fr"].isin(colors)]
        else:
            stamps = stamps[stamps["color_en"].isin(colors)]
    if value is not None:
        if language[0:2] == "fr":
            stamps = stamps[stamps["value_fr"] == value]
        else:
            stamps = stamps[stamps["value_en"] == value]
    if stamp_type is not None:
        types = stamp_type.split(',')
        stamps = stamps[stamps["type_fr"].isin(types)]
    if start is not None:
        i = start - 1
    else:
        i = 0
    if count is not None:
        stamps = stamps[i:i+count]

    # Convert all items in stamps to dicts that can be validated as Stamp model objects.
    apistamps = stamps.to_dict(orient='records')
    for d in apistamps:
        convert_db_stamp_to_api_stamp(d)
    result = {"count": len(apistamps),
              "stamps": apistamps}
    toc = time.perf_counter_ns()
    # Return total server xecution time in milliseconds (not including FastAPI itself)
    response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/stamps/{stamp_id}", status_code=status.HTTP_200_OK, tags=["stamps"])
def get_stamp(response: Response,
              stamp_id: str = Path(description="""`stamp_id` is the unique id of the stamp in the
                                                  format T-N-V or T-N, where T is type, N is the
                                                  Yvert-Tellier catalog number and V is the
                                                  variant. N is a number and V is usually a lower
                                                  case letter. Note that `stamp_id` may contain
                                                  whitespaces. Eg.
                                                  '/stamps/Pour la poste Aérienne-65'""")) \
              -> StampWithVariants | None:
    """Return the stamp with the given `stamp_id`."""
    global indexed_db
    tic = time.perf_counter_ns()
    # First we check that we have a valid stamp_id
    items = stamp_id.split("-")
    if len(items) < 2 or len(items) > 3:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Return total server xecution time in milliseconds (not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return None
    elif len(items) == 2:
        yt_type, yt_no = items
        yt_variant = ""
    else:  # len(items) == 3:
        yt_type, yt_no, yt_variant = items
    # Now we look up the stamp
    try:
        # Get the stamp
        stamp = indexed_db.loc[(yt_type, yt_no, yt_variant)]
        d = stamp.to_dict()
        # Add the stamp id attributes to the stamp
        d["id"] = {"yt_no": yt_no,
                   "yt_variant": yt_variant,
                   "type": yt_type}
        # Add the URL to the stamp
        d["url"] = f"stamps/{stamp_id}"
        # Get all variants of the stamp
        df = indexed_db.loc[(yt_type, yt_no)]
        variants = df.to_dict('index')
        if len(variants) == 1:
            d["variants"] = None
        else:
            d["variants"] = variants
            # Add the stamp id attributes to all the stamp variants
            for var, varstamp in variants.items():
                if var == " ":
                    varstamp["id"] = {"yt_no": yt_no,
                                      "yt_variant": "",
                                      "type": yt_type}
                else:
                    varstamp["id"] = {"yt_no": yt_no,
                                      "yt_variant": var,
                                      "type": yt_type}
        result = StampWithVariants.model_validate(d)
        toc = time.perf_counter_ns()
        # Return total server xecution time in milliseconds (not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return result

    except KeyError:
        response.status_code = status.HTTP_404_NOT_FOUND
        toc = time.perf_counter_ns()
        # Return total server xecution time in milliseconds (not including FastAPI itself)
        response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
        return None


@app.get("/stamps/{stamp_id}/image", status_code=status.HTTP_200_OK, tags=["stamps"])
def get_stamp_image(response: Response, stamp_id: str = Path(description="""`stamp_id` is a unique
                                                                            id of the stamp in the
                                                                            format T-N-V, where T is
                                                                            type, N is the Yvert-
                                                                            Tellier catalog
                                                                            number. Note that it may
                                                                            contain whitespaces.
                                                                            E.g. '/stamps/Pour la
                                                                            poste Aérienne-65'""")):
    """Return the image of the stamp with the given `stamp_id`."""
    global indexed_db
    tic = time.perf_counter_ns()
    if os.path.exists(settings.STAMP_CATALOG_IMAGES_DIR):
        # First we check that we have a valid stamp_id
        items = stamp_id.split("-")
        if len(items) < 2 or len(items) > 3:
            response.status_code = status.HTTP_404_NOT_FOUND
            toc = time.perf_counter_ns()
            # Return total server xecution time in milliseconds (not including FastAPI itself)
            response.headers["Server-timing"] = f"API;dur={(toc - tic)/1000000}"
            return None
        elif len(items) == 2:
            yt_type, yt_no = items
            yt_variant = ""
        else:  # len(items) == 3:
            yt_type, yt_no, yt_variant = items
        # Now we look up the stamp
        try:
            # Get the stamp
            stamp = indexed_db.loc[(yt_type, yt_no, yt_variant)]
            d = stamp.to_dict()
            image_path = (os.path.join(settings.STAMP_CATALOG_IMAGES_DIR, d["image"]))
            toc = time.perf_counter_ns()
            # Return total server xecution time in milliseconds (not including FastAPI itself)
            msecs = f"API;dur={(toc-tic)/1000000}"
            return FileResponse(image_path,
                                media_type="image/jpeg",
                                headers={"Server-timing": msecs})

        except KeyError:
            response.status_code = status.HTTP_404_NOT_FOUND
            toc = time.perf_counter_ns()
            # Return total server xecution time in milliseconds (not including FastAPI itself)
            response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
            return None


@app.get("/stamp_titles", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_titles(response: Response,
                     q: Optional[str] = Query(None,
                                              description="""Query string for stamp titles."""),
                     start: Optional[int] = Query(None,
                                                  description="""Return the titles beginning with
                                                                 title at `start` position in the
                                                                 list of title. If not given,
                                                                 `start` is implicitly 1. Must be
                                                                 >= 1."""),
                     count: Optional[int] = Query(None,
                                                  description="""Return the given `count` of titles
                                                                 from the list of titles. If not
                                                                 given, `count` is implicitly 'all'.
                                                                 Must be >= 1."""),
                     accept_language: Optional[str] = Header(None)) -> StringValuesList | str:
    """Return all stamp titles matching the query string `q`."""
    tic = time.perf_counter_ns()
    language = parsed_accept_language(accept_language)[0][0]
    stamps = db
    if language[0:2] == "fr":
        titles_lang = stamps['title_fr']
        response.headers["Content-Language"] = "fr"
    else:
        titles_lang = stamps['title_en']
        response.headers["Content-Language"] = "en"
    # We assume only one star '*' in q
    if q is None or q == "*":
        titles = titles_lang.unique().tolist()
        result = {"count": len(titles),
                  "values": sorted(titles)}
        toc = time.perf_counter_ns()
        # Return total server xecution time in milliseconds (not including FastAPI itself)
        response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
        return result
    if q.count('*') > 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        toc = time.perf_counter_ns()
        # Return total server xecution time in milliseconds (not including FastAPI itself)
        response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
        return "Multiple wildcard stars '*' in query is not supported."
    # titles = pd.Series(db['title'].unique())
    prefix = q[-1] == "*"
    suffix = q[0] == "*"
    if prefix and suffix:
        titles = titles_lang[titles_lang.str.contains(q[1:-1], na=False)].unique().tolist()
    elif prefix:
        titles = titles_lang[titles_lang.str.startswith(q[0:-1], na=False)].unique().tolist()
    elif suffix:
        titles = titles_lang[titles_lang.str.endswith(q[1:], na=False)].unique().tolist()
    else:
        starpos = q.find('*')
        titles = titles_lang[titles_lang.str.startswith(q[0:starpos], na=False)]
        titles = titles[titles.str.endswith(q[starpos+1:], na=False)].unique().tolist()
    result = {"count": len(titles),
              "values": titles}
    toc = time.perf_counter_ns()
    # Return total server xecution time in milliseconds (not including FastAPI itself)
    response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/stamp_years", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_years(response: Response):
    """Return all the years that stamps in the catalog have been issued."""
    tic = time.perf_counter_ns()
    stamps = db
    years = stamps['issued'].unique().tolist()
    result = {"count": len(years),
              "values": sorted(years)}
    toc = time.perf_counter_ns()
    # Return total server xecution time in milliseconds (not including FastAPI itself)
    response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/stamp_colors", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_colors(response: Response,
                     accept_language: Optional[str] = Header(None)):
    """Return all the colors that stamps in the catalog can have."""
    tic = time.perf_counter_ns()
    language = parsed_accept_language(accept_language)[0][0]
    stamps = db
    if language[0:2] == "fr":
        colors_lang = stamps['color_fr']
        response.headers["Content-Language"] = "fr"
    else:
        colors_lang = stamps['color_en']
        response.headers["Content-Language"] = "en"
    colors_lang = colors_lang.unique().tolist()
    result = {"count": len(colors_lang),
              "values": sorted(colors_lang)}
    toc = time.perf_counter_ns()
    # Return total server xecution time in milliseconds (not including FastAPI itself)
    response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
    return result


@app.get("/stamp_values", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_values(response: Response,
                     accept_language: Optional[str] = Header(None)):
    """Return all the printed values that stamps in the catalog can have."""
    tic = time.perf_counter_ns()
    language = parsed_accept_language(accept_language)[0][0]
    stamps = db
    if language[0:2] == "fr":
        values_lang = stamps['value_fr']
        response.headers["Content-Language"] = "fr"
    else:
        values_lang = stamps['value_en']
        response.headers["Content-Language"] = "en"
    values_lang = values_lang.unique().tolist()
    result = {"count": len(values_lang),
              "values": sorted(values_lang)}
    toc = time.perf_counter_ns()
    # Return total server xecution time in milliseconds (not including FastAPI itself)
    response.headers["Server-Timing"] = f"API;dur={(toc - tic)/1000000}"
    return result
