# Property Data

Datasette instance deployed with MA property data for towns around Greenfield.

Data from https://www.mass.gov/info-details/massgis-data-property-tax-parcels

```shell
# create sqlite file from data
$ uv run —script main.py
$ uvx --with datasette-geojson-map --with datasette-leaflet-geojson datasette --load-extension=mod_spatialite property-data.db
$ open http://127.0.0.1:8001/property-data/parcels

# to deploy
$ uvx gcloud auth login
# https://cloud.google.com/build/docs/deploying-builds/deploy-cloud-run#before_you_begin
$ uvx datasette publish cloudrun property-data.db --service property-data --install datasette-geojson-map --install datasette-leaflet-geojson --spatialite
```
