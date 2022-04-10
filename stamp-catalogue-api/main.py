from fastapi import FastAPI, status, Request, Response, Path, Query
from typing import Optional
import pandas as pd
import os.path

description = """
## Faststamps Catalogue API

This is a simple API for retrieving information on stamps in a stamp catalogue.
"""


# Constants
VERSION = "0.0.1"
STAMP_CATALOGUE_CSV_FILE = "./french-stamps.csv"

# Globals. :-# OMG! What did I do!?
db = None


app = FastAPI(
    title="The Faststamps Catalogue API",
    description=description,
    version=VERSION)


@app.on_event("startup")
def startup_event():
    """Initialize the API by initializing the database. That means opening the local CSV-file
       containing a full stamp catalogue and then reading into some suitable in-memory data
       structure."""
    global db
    if os.path.exists(STAMP_CATALOGUE_CSV_FILE):
        with open(STAMP_CATALOGUE_CSV_FILE) as f:
            db = pd.read_csv(f, delimiter=';')


@app.on_event("shutdown")
async def shutdown():
    pass


@app.get("/", tags=["stamps"])
def api_root_resource(request: Request):
    """The root resource. Returns the name of this API and an URL where the OpenAPI specification
       of this API can be found."""
    print(request.url)
    return {"name": "Faststamps Catalogue API.",
            "version": VERSION,
            "openapi-specification": str(request.url) + "docs",
            "health": str(request.url) + "health",
            "resources": {}}


@app.get("/stamps", tags=["stamps"])
def get_stamps(response: Response,
               title: Optional[str] = Query(None, description="""Return stamps that have the given
                                                                 `title`."""),
               year: Optional[str] = Query(None, description="""Return stamps that were issued the
                                                                given `year`. `year` can be a
                                                                comma-separated list of years."""),
               color: Optional[str] = Query(None, description="""Return stamps with the given
                                                                 `color`. `color` can be a
                                                                 comma-separated list of
                                                                 colors."""),
               value: Optional[str] = Query(None, description="""Return stamps with the given
                                                                 printed `value`. `value` can be
                                                                 a comma-separated list of
                                                                 values."""),
               stamp_type: Optional[str] = Query(None, description="""Return stamps of the given
                                                                      `stamp_type`. `stamp_type`
                                                                      can be a comma-separated
                                                                      list of values."""),
               start: Optional[int] = Query(None, description="""Return the stamps beginning with
                                                                 stamp at `start` position in the
                                                                 list of stamps. If not given,
                                                                 `start` is implicitly 1. Must
                                                                 be >= 1."""),
               count: Optional[int] = Query(None, description="""Return the given `count` of stamps
                                                                 from the list of stamps. If not
                                                                 given, `count` is implicitly
                                                                 'all'. Must be >= 1.""")):
    """Return the catalogue of stamps. If no query parameter is specified all stamps in the
       catalogue are returned. All query parameters can be combined.

The query parameters `title`, `year`, `color`, `value` and `stamp_type` can be used to filter
which stamps to return from the catalogue.

The query parameters `start`and `count` control which and how many number of the, possibly
filtered, stamps in the catalogue to return.

Examples:

* `/stamps` will return all stamps.
* `/stamps?title=Marianne` will return all stamps with the name "Marianne".
* `/stamps?year=1931,1932,1933` will return all stamps issued in 1931, 1932 or 1933.
* `/stamps?color=Green,Olive` will return all stamps that are colored "Green" or "Olive".
* `/stamps?value=1 French centime` will return all stamps with the printed value of "1 French
centime".
* `/stamps?stamp_type=timbre` will return all stamps of typ "timbre".
* `/stamps?start=1000` will return all stamps beginning with the 1000:th stamp.
* `/stamps?count=100` will return a maximum of 100 stamps.
    """
    if start is not None and start <= 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.body = "Query parameter 'start' must be >= 1."
        return None
    if count is not None and count <= 0:
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.body = "Query parameter 'count' must be >= 1."
        return None
    # We apply successive filters on the pandas dataFrame `db`
    stamps = db
    if title is not None:
        stamps = stamps[stamps["title"] == title]
    if year is not None:
        years = [int(item) for item in year.split(',')]
        stamps = stamps[stamps["issued"].isin(years)]
    if color is not None:
        colors = color.split(',')
        stamps = stamps[stamps["color"].isin(colors)]
    if value is not None:
        stamps = stamps[stamps["value"] == value]
    if stamp_type is not None:
        types = stamp_type.split(',')
        stamps = stamps[stamps["type"].isin(types)]
    # I should add a column with the URL to each individual stamp and to the URL for the image of
    # each individual stamp
    return {"count": len(stamps.index),
            "stamps": stamps.to_dict(orient='records')}


@app.get("/stamps/{yt}", status_code=status.HTTP_200_OK, tags=["stamps"])
def get_stamp(response: Response, yt: str = Path(None, description="""`yt` is the Yvert-Tellier
                                                                      catalogue number that
                                                                      identifies a specific
                                                                      stamp.""")):
    """Return the stamp with the given Yvert-Tellier catalogue number `yt`."""
    global db
    if yt in db["yt"].values:
        # I should add a column with the URL to the image of the stamp
        return db.loc[(db["yt"] == yt)].to_dict(orient="records")[0]
    else:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None


@app.get("/stamps/{yt}/image", status_code=status.HTTP_200_OK, tags=["stamps"])
def get_stamp_image(response: Response, yt: str = Path(None, description="""`yt` is the
                                                                            Yvert-Tellier catalogue
                                                                            number that identifies
                                                                            a specific stamp.""")):
    """Return the image of the stamp with the given Yvert-Tellier catalogue number `yt`."""
    pass


@app.get("/stamp_titles", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_titles(response: Response, q: Optional[str] = None):
    """Return all the titles that stamps in the catalogue can have."""
    stamps = db
    titles = stamps['title'].unique().tolist()
    # We assume only one star '*' in q
    if q is None or q == "*":
        return {"count": len(titles),
                "titles": sorted(titles)}
    print(q)
    if q.count('*') > 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "Multiple wildcard stars '*' in query is not supported."
    titles = pd.Series(db['title'].unique())
    prefix = q[-1] == "*"
    suffix = q[0] == "*"
    if prefix and suffix:
        titles = titles.loc[titles.str.contains(q[1:-1], na=False)]
    elif prefix:
        titles = titles.loc[titles.str.startswith(q[0:-1], na=False)]
    elif suffix:
        titles = titles.loc[titles.str.endswith(q[1:], na=False)]
    else:
        starpos = q.find('*')
        titles = titles.loc[titles.str.startswith(q[0:starpos], na=False)]
        titles = titles.loc[titles.str.endswith(q[starpos+1:], na=False)]
    return {"count": len(titles),
            "stamp_titles": titles.to_list()}


@app.get("/stamp_years/", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_years(response: Response):
    """Return all the years that stamps in the catalogue have been issued."""
    stamps = db
    years = stamps['issued'].unique().tolist()
    return {"count": len(years),
            "titles": sorted(years)}


@app.get("/stamp_colors/", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_colors(response: Response):
    """Return all the colors that stamps in the catalogue can have."""
    stamps = db
    colors = stamps['color'].unique().tolist()
    return {"count": len(colors),
            "colors": sorted(colors)}


@app.get("/stamp_values/", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_values(response: Response):
    """Return all the printed values that stamps in the catalogue can have."""
    stamps = db
    values = stamps['value'].unique().tolist()
    return {"count": len(values),
            "colors": sorted(values)}
