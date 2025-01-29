# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "beautifulsoup4",
#     "dbfread",
#     "openpyxl>=3.1.5",
#     "pandas",
#     "requests",
#     "rich",
#     "shapefile-to-sqlite",
#     "sqlite-utils",
#     "fiona<1.9",
# ]
# [tool.uv.sources]
# shapefile-to-sqlite = { git = "https://github.com/saulshanabrook/shapefile-to-sqlite", branch = "main" }
# ///

# require only fiona bc of this error
#   File "/Users/saul/Library/Caches/uv/archive-v0/gujtHHy0P_suD2zU4rC6T/lib/python3.11/site-packages/shapefile_to_sqlite/utils.py", line 65, in yield_features
#     feature.pop("type")
#   File "<frozen _collections_abc>", line 912, in pop
#   File "/Users/saul/Library/Caches/uv/archive-v0/gujtHHy0P_suD2zU4rC6T/lib/python3.11/site-packages/fiona/model.py", line 150, in __getitem__
#     return props[item]
#            ~~~~~^^^^^^
# KeyError: 'type'
import functools
import subprocess
import zipfile
from io import BytesIO
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup
from dbfread import DBF
from rich.progress import track
from sqlite_utils import Database

TOWNS = [
    "Greenfield",
    # "Shelburne",
    # "Conway",
    # "Deerfield",
    # "Montague",
    # "Gill",
    # "Bernardston",
    # "Leyden",
    # "Colrain",
    # "Wendell",
    # "Heath",
    # "Northfield",
    # "Buckland",
    # "Shelburne",
    # "Ashfield",
    # "Cummington",
    # "Goshen",
    # "Whately",
    # "Sunderland",
    # "Leverett",
    # "Shutesbury",
    # "New Salem",
    # "Erving",
    # "Charlemont",
]

DB_FILE = "property-data.db"


def get_town_values() -> dict[str, str]:
    page = requests.get(
        "https://dlsgateway.dor.state.ma.us/gateway/DLSPublic/ParcelSearch"
    )
    soup = BeautifulSoup(page.text, "html.parser")
    return {
        o.text: o["value"]
        for o in soup.find(id="SelectedJurisdictions").find_all("option")
    }


def get_sales():
    print("Getting sales")
    Path("data").mkdir(exist_ok=True)
    p = Path("data/LA3ParcelSearch.xlsx")
    if p.exists():
        return
    values = get_town_values()
    data = [("SelectedJurisdictions", values[town]) for town in TOWNS]
    response = requests.post(
        "https://dlsgateway.dor.state.ma.us/gateway/DLSPublic/ParcelSearch/ExportToExcel",
        data=data,
    )
    p.write_bytes(response.content)


@functools.cache
def get_town_download_urls_by_town() -> dict[str, str]:
    # https://www.mass.gov/info-details/massgis-data-property-tax-parcels#downloads-
    download_urls_df = pd.read_excel(
        "https://www.mass.gov/doc/massgis-parcel-data-download-links-table/download"
    )
    download_urls_by_town = {
        r["Town Name"]: r["Shapefile Download URL"]
        for r in download_urls_df.to_dict("records")
    }
    return download_urls_by_town


def main():
    get_sales()
    not_downloaded_towns = [t for t in TOWNS if not list(Path("data").glob(f"*{t}"))]
    for town in track(not_downloaded_towns, "Downloading town data..."):
        url = get_town_download_urls_by_town()[town.upper()]
        r = requests.get(url)
        z = zipfile.ZipFile(BytesIO(r.content))
        z.extractall("data")
    db = Database(DB_FILE, recreate=False)
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
    pd.read_excel(
        "data/LA3ParcelSearch.xlsx", skiprows=4, parse_dates=["Sale Date"]
    ).to_sql("LA3", db.conn, if_exists="append", index=False)

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
