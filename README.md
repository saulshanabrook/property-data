# [Property Data](https://property-data-z2ca4bc27q-ue.a.run.app/property-data/parcels)

Datasette instance deployed with MA property data for towns around Greenfield.

Data from https://www.mass.gov/info-details/massgis-data-property-tax-parcels

```shell
$ main.py
$ datasette publish cloudrun property-data.db --service property-data --install datasette-geojson-map --spatialite
```
