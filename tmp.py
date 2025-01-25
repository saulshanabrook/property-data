import geopandas
from shapely.geometry import Point
from ydata_profiling import ProfileReport

points = [
    Point(625466, 5621289),
    Point(626082, 5621627),
    Point(627116, 5621680),
    Point(625095, 5622358),
]
gdf = geopandas.GeoDataFrame([1, 2, 3, 4], geometry=points, crs=32630)

report = ProfileReport(gdf)

report.to_file("report.html")
