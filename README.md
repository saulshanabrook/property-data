# Property Data

Datasette instance deployed with MA property data for towns around Greenfield.

Data from https://www.mass.gov/info-details/massgis-data-property-tax-parcels

```shell
# create sqlite file from data
$ uv run --script main.py
$ uvx --with datasette-geojson-map --with datasette-leaflet-geojson datasette --load-extension=mod_spatialite --setting sql_time_limit_ms 10000  -i property-data.db
$ open http://127.0.0.1:8001/property-data/parcels
$ open http://127.0.0.1:8001/property-data/sales

# to deploy
$ uvx gcloud auth login
# https://cloud.google.com/build/docs/deploying-builds/deploy-cloud-run#before_you_begin
$ uvx datasette publish cloudrun property-data.db --extra-options "--setting sql_time_limit_ms 10000"  --service property-data --install datasette-geojson-map --install datasette-leaflet-geojson --spatialite
```
