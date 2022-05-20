import subprocess
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from dbfread import DBF
from rich.progress import track
from sqlite_utils import Database

TOWNS = [
    "Greenfield",
    "Shelburne",
    "Conway",
    "Deerfield",
    "Montague",
    "Gill",
    "Bernardston",
    "Leyden",
    "Colrain",
    "Wendell",
]

DB_FILE = "property-data.db"


def get_town_download_urls() -> list[tuple[str, str]]:
    # https://www.mass.gov/info-details/massgis-data-property-tax-parcels#downloads-
    download_urls_df = pd.read_excel(
        "https://www.mass.gov/doc/massgis-parcel-data-download-links-table/download"
    )
    download_urls_by_town = {
        r["Town Name"]: r["Shapefile Download URL"]
        for r in download_urls_df.to_dict("records")
    }
    return [download_urls_by_town[name.upper()] for name in TOWNS]


def main():
    if not list(Path("data").glob("*/*.shp")):
        for url in track(get_town_download_urls(), "Downloading town data..."):
            r = requests.get(url)
            z = zipfile.ZipFile(BytesIO(r.content))
            z.extractall("data")
    db = Database(DB_FILE)
    added_use_codes = False
    for town_dir in track(
        [p for p in Path("data").iterdir() if p.is_dir()], "Converting to sqlite..."
    ):
        for table in ["OthLeg", "TaxPar"]:
            (shp_file,) = town_dir.glob(f"*{table}*.shp")
            subprocess.run(
                [
                    "shapefile-to-sqlite",
                    DB_FILE,
                    "--table",
                    table,
                    str(shp_file),
                    "--spatialite_mod=mod_spatialite.dylib",
                    "--prefix-pk",
                ],
                check=True,
            )
        for table in ["Assess", "UC_LUT"]:
            if table == "UC_LUT":
                if added_use_codes:
                    continue
                added_use_codes = True
            (dbf_file,) = town_dir.glob(f"*{table}*.dbf")
            db[table].insert_all(DBF(dbf_file))
    db.create_view(
        "parcels",
        """
select
  AsGeoJSON(tp.geometry),
  a.BLDG_VAL,
  a.LAND_VAL,
  a.OTHER_VAL,
  a.TOTAL_VAL,
  a.FY,
  a.LOT_SIZE,
  a.LS_DATE,
  a.LS_PRICE,
  a.USE_CODE,
  a.SITE_ADDR,
  a.ADDR_NUM,
  a.FULL_STR,
  a.LOCATION,
  a.CITY,
  a.ZIP,
  a.OWNER1,
  a.OWN_ADDR,
  a.OWN_CITY,
  a.OWN_STATE,
  a.OWN_ZIP,
  a.OWN_CO,
  a.LS_BOOK,
  a.LS_PAGE,
  a.REG_ID,
  a.ZONING,
  a.YEAR_BUILT,
  a.BLD_AREA,
  a.UNITS,
  a.RES_AREA,
  a.STYLE,
  a.STORIES,
  a.NUM_ROOMS,
  a.LOT_UNITS,
  a.CAMA_ID,
  lut.USE_DESC,
  tp.geometry,
  tp.LOC_ID as rowid
from
  Assess a
  inner join TaxPar tp on tp.LOC_ID = a.LOC_ID
  join UC_LUT lut on a.USE_CODE = lut.USE_CODE
""",
        replace=True,
    )
    db.vacuum()


main()

# """
# with props as (
#   select
#     a.BLDG_VAL,
#     a.LAND_VAL,
#     a.OTHER_VAL,
#     a.TOTAL_VAL,
#     a.FY,
#     a.LOT_SIZE,
#     a.LS_DATE,
#     a.LS_PRICE,
#     a.SITE_ADDR,
#     a.ADDR_NUM,
#     a.FULL_STR,
#     a.LOCATION,
#     a.CITY,
#     a.ZIP,
#     a.OWNER1,
#     a.OWN_ADDR,
#     a.OWN_CITY,
#     a.OWN_STATE,
#     a.OWN_ZIP,
#     a.OWN_CO,
#     a.LS_BOOK,
#     a.LS_PAGE,
#     a.REG_ID,
#     a.ZONING,
#     a.YEAR_BUILT,
#     a.BLD_AREA,
#     a.UNITS,
#     a.RES_AREA,
#     a.STYLE,
#     a.STORIES,
#     a.NUM_ROOMS,
#     a.LOT_UNITS,
#     a.CAMA_ID,
#     tp.geometry,
#     tp.LOC_ID as rowid
#   from
#     Assess a
#     inner join TaxPar tp using(LOC_ID)
# ),
# codes as (
#   select
#     a.LOC_ID as rowid,
#     lut.USE_DESC
#   FROM
#     Assess a
#     left join UC_LUT lut using(USE_CODE)
# )
# select
#   *
# from
#   codes
# """
