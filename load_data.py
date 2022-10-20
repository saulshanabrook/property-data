from __future__ import print_function

import sqlite3

import geopandas as gpd
import pandas as pd

__all__ = ['df']

con = sqlite3.connect("property-data.db")
con.enable_load_extension(True)
con.load_extension("mod_spatialite")


# SQL must wrap the geometry in hex(st_asbinary(...))
sql = "SELECT *, Hex(ST_AsBinary(ST_Transform(GEOMETRY, 26986))) as geom FROM parcels;"
df = gpd.GeoDataFrame.from_postgis(sql, con, geom_col="geom").drop(
    ['AsGeoJSON(tp.geometry)', 'geometry'],
    axis=1
)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)
