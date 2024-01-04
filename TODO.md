# TODO

The general roadmap is:

1. Implement a MWV (Minimal Working Version) of the Catalog API. This is to learn more about
   FastAPI and to get a working catalog of stamps to work with.
2. Implement a MWV of the Web app. This is to learn more about HTMX and then also using the
   catalog API.
3. Implement a MWV of the Collections API. This is to get a first MWV of the full application.

Below I list a number of to-dos for the three components.

## Stamp web app

In the first implementation there will be only one user (me) and that account will be managed by the
Collections API. Eventually we will need a separate Accounts API to manage multiple users.

Implement first MWV:
- [X] Implement first HTML layout of index.html and CSS styling with Bulma CSS.
- [X] Dockerify.
- [X] Implement the search view with HTMX using the catalog API with support for searching on English title.
- [X] Add proper logging.

Implement more proper search support:
- [ ] Case insensitive.
- [ ] Search English title with wild card.
- [ ] Search on all words.

Implement search filters:
- [ ] With filtering on stamp type (Poste & Pour la poste Aérienne), years (and year intervals) and color.

Implement sorting results:
- [ ] Sort on yt number forward or backwards.

Implement login:
- [ ] Implement login using the Collections API.

Implement support for collections:
- [ ] Implement updating a collection using the Collections API.
- [ ] Implement the catalog view using the catalog API.

## Stamp catalog API

Currently the API only supports a single catalog. The catalog CSV file to use is also hard coded as a constant in the source code.

- [X] Implement first MWV.
- [X] Specify the stamp catalog file to use via a config file / environment variable.
- [X] Add use of the Server-Timing HTTP header.
- [X] Add API typing based on Pydantic BaseModel.
- [X] Dockerify.
- [ ] Use Pydantic validation on all query parameters.
- [X] Add proper logging.
- [ ] Move the database (reading of the catalog CSV file) to a separate file/module.
- [ ] Use an embedded database (unqlite, tidydb or sqllite).
- [ ] Document the catalog CSV file format (as an inter-system data transfer format).

In the future:
- [ ] Make the API support multiple stamp catalogs. This means API rewrite and redesign.
- [ ] Make it possible to specify and/or add (load) stamp catalogs via the API. Also to download them as CSV-files.
- [ ] Support metadata on the stamp catalogs, i.e. name, source etc.

## Stamp collection API

The stamp collection API will initially not have support for multiple users. But eventually it should.

- [ ] Implement first MWV.
- [ ] Implement support for importing and exporting a collection from/to a CSV file.

In the future:
- [ ] Have support for multiple user collections. We should avoid implementing user accounts in this microservice. That should be a separate microservice.
