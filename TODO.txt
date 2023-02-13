# TODO

## Stamp catalogue API

Currently the API only supports a single catalogue. The catalogue CSV file to use is also hard coded as a constant in the source code. We can improve a lot here:

 [x] Specify the stamp catalog file to use via a config file / environment variable.
 [ ] Move the database (reading of the catalogue CSV file) to a separate file/module.
 [ ] Add proper logging.
 [ ] Make the API support multiple stamp catalogues. This means API rewrite and redesign.
 [ ] Make it possible to specify and/or add (load) stamp catalogues via the API. Also to download them as CSV-files.
 [ ] Support metadata on the stamp cataloges, i.e. name, source etc.

## Stamp collection API

The stamp collection API will initially not have support for multiple users. But eventually it should:

 [ ] Have support for multiple user collections. We should avoid implementing user accounts in this microservice. That should be a separate microservice.
