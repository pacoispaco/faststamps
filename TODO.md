# TODO

The generap roadmap is:

1. Implement a MWV (Minimal Working Version) of the Catalogue API. This is to learn more about
   FastAPI and to get a working catalogue of stamps to work with.
2. Implement a MWV of the Web app. This is to learn more about HTMX and then also using the
   Catalogue API.
3. Implement a MWV of the Collections API. This is to get a first MWV of the full application.

Below I list a number of todos for the three components.

## Stamp web app

In the first implementation there will be only one user (me) and that account will be managed by the
Collections API. Eventually we will need a separate Accounts API to manage multiple users.

- [ ] Implement first MWV [In progress].
- [x] Implement first HTML layout of index.html and CSS styling with Bulma CSS.
- [ ] Dockerify [In progress].
- [ ] Implement the search view with HTMX using the Catalogue API.
- [ ] Implement login using the Collections API.
- [ ] Implement updating a collection using the Collections API.
- [ ] Implement the catalogue view using the Catalogue API.

## Stamp catalogue API

Currently the API only supports a single catalogue. The catalogue CSV file to use is also hard coded as a constant in the source code.

- [x] Implement first MWV.
- [x] Specify the stamp catalog file to use via a config file / environment variable.
- [x] Add use of the Server-Timing HTTP header.
- [x] Add API typing based on Pydantic BaseModel.
- [x] Dockerify.
- [ ] Use Pydantic validation on query parameters.
- [ ] Add proper logging.
- [ ] Move the database (reading of the catalogue CSV file) to a separate file/module.
- [ ] Document the catalogue CSV file format (as a intersystem data transfer format).
- [ ] Make the API support multiple stamp catalogues. This means API rewrite and redesign.
- [ ] Make it possible to specify and/or add (load) stamp catalogues via the API. Also to download them as CSV-files.
- [ ] Support metadata on the stamp cataloges, i.e. name, source etc.

## Stamp collection API

The stamp collection API will initially not have support for multiple users. But eventually it should.

- [ ] Implement first MWV.
- [ ] Implement support for importing and exporting a collection from/to a CSV file.
- [ ] Have support for multiple user collections. We should avoid implementing user accounts in this microservice. That should be a separate microservice.
