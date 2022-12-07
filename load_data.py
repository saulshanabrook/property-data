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
).set_crs(epsg=26986)


pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', 100)


HIDE_USE_DESCS = [
    # "Undevelopable Residential Land",
    # "All land designated under Chapter 61 (not classified as Open Space)",
    "Vacant, Conservation Organizations (Charitable Org.)",
    "Dept. of Fish and Game (DFG) -- formerly Division of Fisheries and Wildlife, Environmental Law Enforcement (DFWELE)",
    "Dept. of Conservation and Recreation (DCR), Division of State Parks and Recreation",
    "Improved, Selectmen or City Council (Municipal)",
    "Vacant, Other District (County)",
    "(formerly Colleges, Schools(private).  Removed June 2009. )",
    "Dept. of Education (DOE) - UMass., State Colleges, Community Colleges",
    "Secondary Level (Educational Private)",
    # "Productive Woodland - woodlots (Ch. 61A, not classified as Open Space)",
    # "Field Crops - hay, wheat, tillable forage, cropland, etc... (Ch. 61A, not classified as Open Space)",
    # "Nature Study - areas specifically for nature study or observation (Ch. 61B, not classified as Open Space)",
    # "Pasture (Ch. 61A, not classified as Open Space)",
    # "Truck Crops - vegetables (Ch. 61A, not classified as Open Space)",
    # "Hiking - trails or paths, Camping - areas with sites for overnight camping, Nature Study (Ch. 61B, not classified as OS)",
    # "Necessary related land-farm roads, ponds, land under farm buildings (Ch. 61A, not classified as Open Space)",
    # "Agricultural/Horticultural Land not included in Chapter 61A",
    # "Hunting - areas for the hunting of wildlife (Ch. 61B, not classified as Open Space)",
    # "Nurseries (Ch. 61A, not classified as Open Space)",
    # "Wet land, scrub land, rock land (Ch. 61A, not classified as Open Space)",
    # "Orchards - pears, apples, grape vineyards, etc... (Ch. 61A, not classified as Open Space)",
    # "Tobacco, Sod (Ch. 61A, not classified as Open Space)",
    # "Camping - areas with sites for overnight camping (Ch. 61B, not classified as Open Space)",
    # "Christmas Trees (Ch. 61A, not classified as Open Space)",
    # "Golfing - areas of land arranged as a golf course (Ch. 61B, not classified as Open Space)",
    # "Horseback Riding - trails or areas (Ch. 61B, not classified as Open Space)",
    "Vacant, Selectmen or City Council (Municipal)",
    "Vacant, District (County)",
    "Vacant, Conservation (Municipal or County)",
    "Electric Transmission Right-of-Way",
    "(formerly Charitable Organizations (private hospitals, etc...).  Removed June 2009. )",
    "(formerly Municipalities/Districts.  Removed June 2009.)",
    "(formerly Commonwealth of Massachusetts.  Removed June 2009.)",
    # "Undevelopable Commercial Land",
    "Dept. of Conservation and Recreation (DCR) - Division of Water Supply Protection",
    "Housing Authority",
    "Other",
    "Cemeteries (Charitable Org.)",
    "Hospitals (Charitable Org.)",
    "Recreation, Active Use (Charitable Org.)",
    "Improved County or Regional Correctional",
    "United States Government"
    # "Undevelopable Industrial Land"
]

HIDE_OWNERS = [
    "WESTERN MASS ELECTRIC",
    "GREENFIELD TOWN OF",
    "COMMONWEALTH OF MASS DIV OF CAPITAL PLANNING",
    "GREENFIELD CORPORATE CENTER LLC"
]