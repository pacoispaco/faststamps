from fastapi import FastAPI, status, Request, Response, Path, Query, Header
from typing import Optional
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import os.path

description = """
## Faststamps Catalogue API

This is a simple API for retrieving information on stamps in a stamp catalogue.
"""


load_dotenv()

# Constants and environment variables
VERSION = "0.0.1"
STAMP_CATALOGUE_CSV_FILE = os.environ.get("STAMP_CATALOGUE_CSV_FILE")

# Globals. :-# OMG! What did I do!?
# These "databases" are simply Pandas Dataframes. One holds the stamps CSV file and the other simply
# is an indexed version of the former.
db = None
indexed_db = None

# Utility functions
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
    title="The Faststamps Catalogue API",
    description=description,
    version=VERSION)


@app.on_event("startup")
def startup_event():
    """Initialize the API by initializing the database. That means opening the local CSV-file
       containing a full stamp catalogue and then reading into some suitable in-memory data
       structure."""
    global db, indexed_db
    if os.path.exists(STAMP_CATALOGUE_CSV_FILE):
        with open(STAMP_CATALOGUE_CSV_FILE) as f:
            db = pd.read_csv(f, delimiter=';', dtype = {'issued': str, 'id-yt-no': str})
            # We replace all np.NAN with an empty string "" and create a multindex
            # consisting of the stamp type, Yt no and variant.
            db = db.replace({np.NaN:""})
            # Add URL column
            db["url"] = db[["type-fr", "id-yt-no", "id-yt-var"]].apply(lambda x: f"stamps/{x[0]}-{x[1]}-{x[2]}" if x[2] else f"stamps/{x[0]}-{x[1]}", axis=1)
            indexed_db = db.set_index(["type-fr", "id-yt-no", "id-yt-var"])
            indexed_db = indexed_db.sort_index()
            print(indexed_db.loc[("Poste", "1", "")].to_dict)
            print(indexed_db.loc[("Poste", "1", "a")].to_dict)

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
                                                           the list of stamps. If not given, `count`
                                                           is implicitly 'all'. Must be >= 1."""),
               accept_language: Optional[str] = Header(None)):
    """Return the catalogue of stamps. If no query parameter is specified all stamps in the
       catalogue are returned. All query parameters can be combined.

The query parameters `title`, `year`, `color`, `value` and `stamp_type` can be used to filter
which stamps to return from the catalogue.

The query parameters `start`and `count` control which and how many number of the, possibly
filtered, stamps in the catalogue to return.

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
    language = parsed_accept_language(accept_language)[0][0]
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
        if language[0:2] == "fr":
            stamps = stamps[stamps["title-fr"] == title]
        else:
            stamps = stamps[stamps["title-en"] == title]
    if issued is not None:
        issued_years = [item for item in issued.split(',')]
        print(issued_years)
        stamps = stamps[stamps["issued"].isin(issued_years)]
    if color is not None:
        colors = color.split(',')
        if language[0:2] == "fr":
            stamps = stamps[stamps["color-fr"].isin(colors)]
        else:
            stamps = stamps[stamps["color-en"].isin(colors)]
    if value is not None:
        if language[0:2] == "fr":
            stamps = stamps[stamps["value-fr"] == value]
        else:
            stamps = stamps[stamps["value-en"] == value]
    if stamp_type is not None:
        types = stamp_type.split(',')
        stamps = stamps[stamps["type-fr"].isin(types)]
    # I should add a column with the URL to each individual stamp and to the URL for the image of
    # each individual stamp
    return {"count": len(stamps.index),
            "stamps": stamps.to_dict(orient='records')}

@app.get("/stamps/{stamp_id}", status_code=status.HTTP_200_OK, tags=["stamps"])
def get_stamp(response: Response, stamp_id: str = Path(None, description="""`stamp_id` is a unique
                                                                            id of the stamp in the
                                                                            format T-N-V, where T
                                                                            is type, N is the
                                                                            Yvert-Tellier catalogue
                                                                            number. Note that it may
                                                                            contain whitespaces.
                                                                            E.g. '/stamps/Pour la
                                                                            poste Aérienne-65'""")):
    """Return the stamp with the given `stamp_id`i."""
    global indexed_db
    # First we check that we have a valid stamp_id
    items = stamp_id.split("-")
    if len(items) < 2 or len (items) > 3:
        response.status_code = status.HTTP_404_NOT_FOUND
        return None
    elif len(items) == 2:
        yt_type, yt_no = items
        yt_variant = ""
    else: # len(items) == 3:
        yt_type, yt_no, yt_variant = items
    # Now we look up the stamp
    try:
        print("yt_type: '%s'" % (yt_type))
        print("yt_no: '%s'" % (yt_no))
        print("yt_variant: '%s'" % (yt_variant))
        # Get the stamp (Pandas Series)
        stamp = indexed_db.loc[(yt_type, yt_no, yt_variant)]
        print (stamp)
        d = stamp.to_dict()
        # Add the stamp id attributes to the stamp
        d["id"] = {"yt-no": yt_no,
                   "yt-variant": yt_variant,
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

        import pprint
        pprint.pprint(d)
        return d

    except KeyError:
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
                     accept_language: Optional[str] = Header(None)):
    """Return all stamp titles matching the query string `q`."""
    language = parsed_accept_language(accept_language)[0][0]
    stamps = db
    if language[0:2] == "fr":
        titles_lang = stamps['title-fr']
        response.headers["Content-Language"] = "fr"
    else:
        titles_lang = stamps['title-en']
        response.headers["Content-Language"] = "en"
    # We assume only one star '*' in q
    if q is None or q == "*":
        titles = titles_lang.unique().tolist()
        return {"count": len(titles),
                "titles": sorted(titles)}
    if q.count('*') > 1:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "Multiple wildcard stars '*' in query is not supported."
    #titles = pd.Series(db['title'].unique())
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
    return {"count": len(titles),
            "stamp_titles": titles}


@app.get("/stamp_years", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_years(response: Response):
    """Return all the years that stamps in the catalogue have been issued."""
    stamps = db
    years = stamps['issued'].unique().tolist()
    return {"count": len(years),
            "titles": sorted(years)}


@app.get("/stamp_colors", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_colors(response: Response,
                     accept_language: Optional[str] = Header(None)):
    """Return all the colors that stamps in the catalogue can have."""
    language = parsed_accept_language(accept_language)[0][0]
    stamps = db
    if language[0:2] == "fr":
        colors_lang = stamps['color-fr']
        response.headers["Content-Language"] = "fr"
    else:
        colors_lang = stamps['color-en']
        response.headers["Content-Language"] = "en"
    colors_lang = colors_lang.unique().tolist()
    return {"count": len(colors_lang),
            "colors": sorted(colors_lang)}


@app.get("/stamp_values", status_code=status.HTTP_200_OK, tags=["stamp attributes"])
def get_stamp_values(response: Response,
                     accept_language: Optional[str] = Header(None)):
    """Return all the printed values that stamps in the catalogue can have."""
    language = parsed_accept_language(accept_language)[0][0]
    stamps = db
    if language[0:2] == "fr":
        values_lang = stamps['value-fr']
        response.headers["Content-Language"] = "fr"
    else:
        values_lang = stamps['value-en']
        response.headers["Content-Language"] = "en"
    values_lang = values_lang.unique().tolist()
    return {"count": len(values_lang),
            "colors": sorted(values_lang)}
